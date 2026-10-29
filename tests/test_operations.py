"""설치 묶음, 읽기 전용 점검, 평가 증거, 커밋 기반 배포의 경계를 검증한다."""
import hashlib
import io
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import profiles
import doctor
import build_release
import validate_repo
import audit_tools

spec = importlib.util.spec_from_file_location('selection', ROOT / 'evals/run_selection.py')
selection = importlib.util.module_from_spec(spec)
spec.loader.exec_module(selection)


class TemporaryTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=os.environ.get('KIT_TEST_ROOT'))
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)


class ProfilesTest(TemporaryTest):
    def test_union_and_unknown_profile(self):
        expected = set(profiles.load_profiles(ROOT)['web']['skills'])
        self.assertEqual(set(profiles.expand(ROOT, ['core', 'web', 'web'], [])), expected)
        with self.assertRaises(ValueError):
            profiles.expand(ROOT, ['missing'], [])

    def test_invalid_entry_is_controlled_error(self):
        (self.root / 'profiles.json').write_text(json.dumps({'schema': 1, 'profiles': {
            'bad': {'description': 'bad', 'skills': [{}]}}}), encoding='utf-8')
        with self.assertRaises(ValueError):
            profiles.load_profiles(self.root)

    def test_install_profile_repeat_preserves_rules_and_config(self):
        home, skills = self.root / 'home', self.root / 'skills'
        home.mkdir()
        (home / 'AGENTS.md').write_bytes(b'local rules')
        (home / 'config.toml').write_bytes(b'local config')
        args = [sys.executable, '-B', str(ROOT / 'scripts/install.py'),
                '--codex-home', str(home), '--skills-root', str(skills),
                '--profile', 'core', '--profile', 'video', '--skip-rules']
        dry = subprocess.run(args + ['--dry-run'], capture_output=True)
        self.assertEqual(dry.returncode, 0, dry.stderr)
        self.assertFalse(skills.exists())
        for _ in range(2):
            result = subprocess.run(args, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((home / 'AGENTS.md').read_bytes(), b'local rules')
        self.assertEqual((home / 'config.toml').read_bytes(), b'local config')
        self.assertEqual({p.parent.name for p in skills.glob('*/SKILL.md')},
                         set(profiles.load_profiles(ROOT)['video']['skills']))


class DoctorTest(TemporaryTest):
    @patch.object(doctor, 'probe', return_value={'available': False})
    def test_missing_environment_is_not_created(self, _):
        result = doctor.inspect_environment(ROOT, self.root / 'home', [self.root / 'skills'], 'core')
        self.assertEqual({s['status'] for s in result['skills']}, {'missing'})
        self.assertEqual(list(self.root.iterdir()), [])
        self.assertTrue(result['read_only'])

    @patch.object(doctor, 'probe', return_value={'available': True})
    def test_duplicate_cache_and_incomplete_runtime(self, _):
        a, b, home = (self.root / n for n in ('a', 'b', 'home'))
        name = 'minwoo-project-context'
        for dest in (a, b):
            shutil.copytree(ROOT / 'skills' / name, dest / name)
        cache = a / name / '__pycache__/generated.pyc'
        cache.parent.mkdir(); cache.write_bytes(b'cache')
        runtime = home / '.minwoo-codex-kit/runtimes/partial'
        runtime.mkdir(parents=True)
        before = {str(p): (p.read_bytes(), p.stat().st_mtime_ns) for p in self.root.rglob('*') if p.is_file()}
        result = doctor.inspect_environment(ROOT, home, [a, b], 'core')
        after = {str(p): (p.read_bytes(), p.stat().st_mtime_ns) for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before, after)
        self.assertEqual(result['duplicates'], [name])
        self.assertEqual(result['runtimes'], [{'id': 'partial', 'status': 'incomplete'}])
        single = doctor.inspection.inspect(ROOT, home, [a])
        row = next(x for x in single['skills'] if x['skill'] == name)
        self.assertEqual(row['extra'], [])


class SelectionGradeTest(unittest.TestCase):
    catalog = {'one': '---\nname: one\n---\nFull body', 'two': 'Another full skill'}

    def events(self, output, code=0, kind='command_execution'):
        return [{'type': 'item.completed', 'item': {'type': kind, 'exit_code': code,
                'aggregated_output': output}}, {'type': 'turn.completed'}]

    def test_requires_successful_complete_read(self):
        for output, code, kind in [('one', 0, 'command_execution'),
                                   (self.catalog['one'], 1, 'command_execution'),
                                   (self.catalog['one'], 0, 'agent_message')]:
            self.assertFalse(selection.grade(self.events(output, code, kind), self.catalog, ['one'])['passed'])
        self.assertTrue(selection.grade(self.events(self.catalog['one']), self.catalog, ['one'])['passed'])

    def test_unexpected_forbidden_and_incomplete_fail(self):
        events = self.events('\n'.join(self.catalog.values()))
        self.assertFalse(selection.grade(events, self.catalog, ['one'])['passed'])
        self.assertTrue(selection.grade(events, self.catalog, ['one', 'two'])['passed'])
        self.assertFalse(selection.grade(events[:-1], self.catalog, ['one', 'two'])['passed'])
        events += [{'type': 'item.completed', 'item': {'type': 'file_change'}}]
        self.assertFalse(selection.grade(events, self.catalog, ['one', 'two'])['passed'])
        self.assertTrue(selection.grade(self.events('answer'), self.catalog, [])['passed'])


class AuditTest(TemporaryTest):
    def test_partial_or_error_response_does_not_pass(self):
        requirements = self.root / 'requirements.txt'
        requirements.write_text('example==1.0\n', encoding='utf-8')
        for result in ({'results': []}, {'results': [{'error': 'unavailable'}]}):
            with patch.object(audit_tools.urllib.request, 'urlopen', return_value=io.BytesIO(json.dumps(result).encode())):
                with self.assertRaises(ValueError): audit_tools.audit(requirements)
        result = {'results': [{'vulns': [{'id': 'EXAMPLE-1'}]}]}
        with patch.object(audit_tools.urllib.request, 'urlopen', return_value=io.BytesIO(json.dumps(result).encode())):
            self.assertEqual(audit_tools.audit(requirements)[0]['advisories'], ['EXAMPLE-1'])


@unittest.skipUnless(shutil.which('git'), 'Git required')
class ReleaseTest(TemporaryTest):
    def setUp(self):
        super().setUp()
        self.repo = self.root / 'repo'; self.repo.mkdir()
        self.patcher = patch.object(build_release, 'ROOT', self.repo)
        self.patcher.start(); self.addCleanup(self.patcher.stop)
        self.git('init', '-q')
        (self.repo / 'VERSION').write_bytes(b'1.2.3\n')
        self.commit()

    def git(self, *args):
        return subprocess.check_output(['git', '-c', 'user.name=Kit Test', '-c',
                'user.email=kit@example.invalid', *args], cwd=self.repo, stderr=subprocess.STDOUT)

    def commit(self):
        self.git('add', '.')
        self.git('commit', '-qm', 'fixture')

    def test_only_committed_bytes_and_checksums(self):
        (self.repo / 'VERSION').write_text('9.9.9\n', encoding='utf-8')
        (self.repo / 'private.txt').write_text('untracked', encoding='utf-8')
        out = self.root / 'release'
        result = build_release.build(out, expected_tag='v1.2.3')
        self.assertEqual(result['version'], '1.2.3')
        with zipfile.ZipFile(out / 'minwoo-codex-kit-1.2.3.zip') as z:
            self.assertEqual(z.read('minwoo-codex-kit/VERSION'), self.git('show', 'HEAD:VERSION'))
            self.assertNotIn('minwoo-codex-kit/private.txt', z.namelist())
        for line in (out / 'SHA256SUMS').read_text().splitlines():
            digest, name = line.split('  ')
            self.assertEqual(digest, hashlib.sha256((out / name).read_bytes()).hexdigest())
        before = (out / 'SHA256SUMS').read_bytes()
        with self.assertRaises(ValueError): build_release.build(out)
        self.assertEqual(before, (out / 'SHA256SUMS').read_bytes())

    def test_wrong_tag_and_tracked_private_file_rejected(self):
        with self.assertRaises(ValueError):
            build_release.build(self.root / 'bad-tag', expected_tag='v2.0.0')
        (self.repo / 'auth.json').write_text('{}', encoding='utf-8'); self.commit()
        with self.assertRaises(ValueError): build_release.build(self.root / 'bad-file')
        self.assertFalse(list((self.root / 'bad-file').glob('*.zip')))

    def test_relative_sibling_output_is_allowed(self):
        previous = Path.cwd()
        try:
            os.chdir(self.repo)
            build_release.build(Path('../sibling'))
        finally:
            os.chdir(previous)
        self.assertTrue((self.root / 'sibling/SHA256SUMS').is_file())


if __name__ == '__main__':
    unittest.main()
