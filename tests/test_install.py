"""실제 개인 설정을 건드리지 않는 격리된 파일시스템 통합 테스트."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'install.py'
spec = importlib.util.spec_from_file_location('kit_install', SCRIPT)
kit = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = kit
spec.loader.exec_module(kit)


class InstallTests(unittest.TestCase):
    def setUp(self):
        test_dir = os.environ.get('KIT_TEST_ROOT')
        self.temp = tempfile.TemporaryDirectory(prefix='kit-', dir=os.path.abspath(test_dir) if test_dir else None)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).absolute()
        self.repo = self.root / 'source kit'
        self.codex = self.root / 'user space' / '.codex'
        self.skills = self.root / 'user space' / '.agents' / 'skills'
        self.project = self.root / 'project with spaces'
        self.project.mkdir()
        self.write(self.repo / 'VERSION', b'0.1.0\n')
        self.write(self.repo / 'global' / 'AGENTS.md', '공통 규칙\n'.encode())
        self.write(self.repo / 'templates' / 'AGENTS.md', '프로젝트 시작\n'.encode())
        self.write(self.repo / 'skills' / 'example' / 'SKILL.md', b'---\nname: example\ndescription: Example\n---\nTask\n')
        self.write(self.repo / 'skills' / 'other' / 'SKILL.md', b'Other\n')
        self.out = io.StringIO()

    def write(self, path, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def run_install(self, **kwargs):
        options = {'codex_home': self.codex, 'skills_root': self.skills}
        options.update(kwargs)
        with contextlib.redirect_stdout(self.out), contextlib.redirect_stderr(self.out):
            return kit.install(self.repo, **options)

    def snapshot(self):
        return {str(p.relative_to(self.root)): (p.read_bytes(), p.stat().st_mtime_ns)
                for p in self.root.rglob('*') if p.is_file()}

    def make_link(self, link, target, directory=False):
        link.parent.mkdir(parents=True, exist_ok=True)
        try:
            link.symlink_to(target, target_is_directory=directory)
        except OSError:
            if os.name != 'nt' or not directory:
                self.skipTest('File symlinks require host privileges')
            result = subprocess.run(['cmd', '/c', 'mklink', '/J', str(link), str(target)],
                                    capture_output=True)
            if result.returncode:
                self.skipTest('Directory junctions unavailable on host')

    def test_dry_run_writes_nothing(self):
        before = self.snapshot()
        self.run_install(skills=['example'], dry_run=True)
        self.assertEqual(before, self.snapshot())
        self.assertFalse(self.codex.exists())
        self.assertIn('생성 예정', self.out.getvalue())

    def test_rules_only_is_default(self):
        self.run_install()
        self.assertEqual((self.codex / 'AGENTS.md').read_bytes(), '공통 규칙\n'.encode())
        self.assertFalse(self.skills.exists())

    def test_selected_skills_and_unrelated_settings(self):
        config = self.codex / 'config.toml'
        self.write(config, b'approval_policy = "on-request"\n')
        self.write(self.skills / 'existing' / 'SKILL.md', b'keep')
        self.run_install(skills=['example'])
        self.assertTrue((self.skills / 'example' / 'SKILL.md').is_file())
        self.assertFalse((self.skills / 'other').exists())
        self.assertEqual(config.read_bytes(), b'approval_policy = "on-request"\n')
        self.assertEqual((self.skills / 'existing' / 'SKILL.md').read_bytes(), b'keep')

    def test_repeat_install_is_noop_including_state_and_backups(self):
        self.run_install(skills=['example'])
        before = self.snapshot()
        self.run_install(skills=['example'])
        self.assertEqual(before, self.snapshot())

    @unittest.skipUnless(os.name == 'nt', 'Windows case-insensitive paths')
    def test_windows_path_case_does_not_lose_managed_ownership(self):
        self.run_install(skills=['example'])
        self.write(self.repo / 'global' / 'AGENTS.md', b'updated rule')
        self.run_install(codex_home=str(self.codex).upper(), skills_root=str(self.skills).upper(), skills=['example'])
        self.assertEqual((self.codex / 'AGENTS.md').read_bytes(), b'updated rule')

    def test_identical_existing_file_can_be_adopted_without_rewrite(self):
        target = self.codex / 'AGENTS.md'
        self.write(target, (self.repo / 'global' / 'AGENTS.md').read_bytes())
        before = target.stat().st_mtime_ns
        self.run_install()
        self.assertEqual(before, target.stat().st_mtime_ns)
        self.assertTrue((self.codex / kit.STATE_DIR / 'state.json').is_file())

    def test_conflict_aborts_entire_plan_before_writes(self):
        self.write(self.skills / 'example' / 'SKILL.md', b'personal skill')
        before = self.snapshot()
        with self.assertRaises(kit.InstallError):
            self.run_install(skills=['example'])
        self.assertEqual(before, self.snapshot())
        self.assertFalse(self.codex.exists())

    def test_local_edit_is_preserved(self):
        self.run_install(skills=['example'])
        self.write(self.codex / 'AGENTS.md', b'my local change')
        before = self.snapshot()
        with self.assertRaises(kit.InstallError):
            self.run_install(skills=['example'])
        self.assertEqual(before, self.snapshot())

    def test_explicit_replacement_saves_exact_backup_and_mapping(self):
        self.write(self.codex / 'AGENTS.md', b'private original\r\n')
        self.run_install(replace_existing=True)
        maps = list((self.codex / kit.STATE_DIR / 'backups').glob('*/restore-map.json'))
        self.assertEqual(len(maps), 1)
        entries = json.loads(maps[0].read_text(encoding='utf-8'))
        entry = next(e for e in entries if e['target'] == str(self.codex / 'AGENTS.md'))
        self.assertEqual((maps[0].parent / entry['backup']).read_bytes(), b'private original\r\n')

    def test_managed_update_needs_no_force_and_backs_up_previous_version(self):
        self.run_install(skills=['example'])
        target = self.skills / 'example' / 'SKILL.md'
        original = target.read_bytes()
        self.write(self.repo / 'skills' / 'example' / 'SKILL.md', b'updated skill')
        self.run_install(skills=['example'])
        self.assertEqual(target.read_bytes(), b'updated skill')
        backups = list((self.codex / kit.STATE_DIR / 'backups').glob('*/*.bak'))
        self.assertIn(original, [p.read_bytes() for p in backups])

    def test_skip_rules_and_unselected_skills_are_preserved(self):
        self.run_install(skills=['example'])
        self.write(self.codex / 'AGENTS.md', b'local override')
        self.run_install(skills=['other'], skip_rules=True)
        self.assertEqual((self.codex / 'AGENTS.md').read_bytes(), b'local override')
        self.assertTrue((self.skills / 'example' / 'SKILL.md').is_file())

    def test_removed_source_files_are_not_deleted_from_destination(self):
        source = self.repo / 'skills' / 'example' / 'references' / 'note.md'
        self.write(source, b'kept')
        self.run_install(skills=['example'])
        source.unlink()
        self.run_install(skills=['example'])
        self.assertEqual((self.skills / 'example' / 'references' / 'note.md').read_bytes(), b'kept')

    def test_project_scope_uses_template_and_repo_skills(self):
        self.run_install(scope='project', project=self.project, codex_home=None, skills_root=None,
                         skills=['example'])
        self.assertEqual((self.project / 'AGENTS.md').read_bytes(), '프로젝트 시작\n'.encode())
        self.assertTrue((self.project / '.agents' / 'skills' / 'example' / 'SKILL.md').is_file())
        self.assertFalse(self.codex.exists())

    def test_existing_project_rules_are_preserved(self):
        self.write(self.project / 'AGENTS.md', b'team policy')
        with self.assertRaises(kit.InstallError):
            self.run_install(scope='project', project=self.project, codex_home=None, skills_root=None)
        self.assertEqual((self.project / 'AGENTS.md').read_bytes(), b'team policy')

    def test_codex_home_env_does_not_move_official_user_skills(self):
        fake_home = self.root / 'fake home'
        with patch.dict(os.environ, {'CODEX_HOME': str(self.codex)}), patch.object(Path, 'home', return_value=fake_home):
            self.run_install(codex_home=None, skills_root=None, skills=['example'])
        self.assertTrue((self.codex / 'AGENTS.md').is_file())
        self.assertTrue((fake_home / '.agents' / 'skills' / 'example' / 'SKILL.md').is_file())
        self.assertFalse((self.codex / 'skills').exists())

    def test_override_warns_without_altering_override(self):
        target = self.codex / 'AGENTS.override.md'
        self.write(target, b'override')
        self.run_install()
        self.assertIn('우선 적용', self.out.getvalue())
        self.assertEqual(target.read_bytes(), b'override')

    def test_invalid_selection_and_path_traversal_abort(self):
        for name in ('../escape', '/absolute', 'unknown', 'a\\b'):
            with self.subTest(name=name), self.assertRaises(kit.InstallError):
                self.run_install(skills=[name])
        self.assertFalse(self.codex.exists())

    def test_empty_selection_and_invalid_scope_options_abort(self):
        options = [dict(skip_rules=True), dict(project=self.project),
                   dict(scope='project', project=self.project),
                   dict(scope='project', project=None, codex_home=None, skills_root=None)]
        for args in options:
            with self.subTest(args=args), self.assertRaises(kit.InstallError):
                self.run_install(**args)

    def test_source_overlap_is_rejected(self):
        with self.assertRaises(kit.InstallError):
            self.run_install(codex_home=self.repo)

    def test_corrupt_state_is_not_overwritten_even_with_replace(self):
        state = self.codex / kit.STATE_DIR / 'state.json'
        self.write(state, b'{not json')
        before = self.snapshot()
        with self.assertRaises(kit.InstallError):
            self.run_install(replace_existing=True)
        self.assertEqual(before, self.snapshot())

    def test_directory_in_place_of_target_is_rejected(self):
        (self.codex / 'AGENTS.md').mkdir(parents=True)
        with self.assertRaises(kit.InstallError):
            self.run_install(replace_existing=True)

    def test_lock_prevents_concurrent_install(self):
        self.run_install()
        self.write(self.repo / 'global' / 'AGENTS.md', b'new')
        self.write(self.codex / kit.STATE_DIR / 'install.lock', b'')
        before = self.snapshot()
        with self.assertRaises(kit.InstallError):
            self.run_install()
        self.assertEqual(before, self.snapshot())

    def test_write_failure_rolls_back_installed_files_and_state(self):
        self.run_install(skills=['example'])
        target = self.codex / 'AGENTS.md'
        skill = self.skills / 'example' / 'SKILL.md'
        state = self.codex / kit.STATE_DIR / 'state.json'
        before = {p: p.read_bytes() for p in (target, skill, state)}
        self.write(self.repo / 'global' / 'AGENTS.md', b'new rule')
        self.write(self.repo / 'skills' / 'example' / 'SKILL.md', b'new skill')
        real_write = kit.atomic_write
        def fail_once(path, data, mode=0o600):
            if path == skill and data == b'new skill':
                raise OSError('simulated disk error')
            return real_write(path, data, mode)
        with patch.object(kit, 'atomic_write', side_effect=fail_once), self.assertRaises(OSError):
            self.run_install(skills=['example'])
        self.assertEqual(before, {p: p.read_bytes() for p in before})
        self.assertFalse((self.codex / kit.STATE_DIR / 'install.lock').exists())

    def test_new_files_removed_when_state_write_fails(self):
        real_write = kit.atomic_write
        def fail_state(path, data, mode=0o600):
            if path.name == 'state.json':
                raise OSError('simulated state error')
            return real_write(path, data, mode)
        with patch.object(kit, 'atomic_write', side_effect=fail_state), self.assertRaises(OSError):
            self.run_install(skills=['example'])
        self.assertFalse((self.codex / 'AGENTS.md').exists())
        self.assertFalse((self.skills / 'example' / 'SKILL.md').exists())

    def test_concurrent_edit_is_not_overwritten_during_rollback(self):
        self.run_install(skills=['example'])
        target = self.codex / 'AGENTS.md'
        skill = self.skills / 'example' / 'SKILL.md'
        self.write(self.repo / 'global' / 'AGENTS.md', b'new rule')
        self.write(self.repo / 'skills' / 'example' / 'SKILL.md', b'new skill')
        real_write = kit.atomic_write
        def edit_then_fail(path, data, mode=0o600):
            if path == skill and data == b'new skill':
                target.write_bytes(b'another editor')
                raise OSError('simulated concurrent edit')
            return real_write(path, data, mode)
        with patch.object(kit, 'atomic_write', side_effect=edit_then_fail), self.assertRaises(OSError):
            self.run_install(skills=['example'])
        self.assertEqual(target.read_bytes(), b'another editor')
        self.assertIn('수동 복구', self.out.getvalue())

    def test_destination_parent_link_is_rejected_even_with_replace(self):
        outside = self.root / 'outside'
        outside.mkdir()
        link = self.root / 'linked'
        self.make_link(link, outside, directory=True)
        with self.assertRaises(kit.InstallError):
            self.run_install(codex_home=link / '.codex', replace_existing=True)
        self.assertEqual(list(outside.iterdir()), [])

    def test_source_skill_link_is_rejected(self):
        outside = self.root / 'outside skill'
        self.write(outside / 'SKILL.md', b'external skill')
        self.make_link(self.repo / 'skills' / 'linked', outside, directory=True)
        with self.assertRaises(kit.InstallError):
            self.run_install(skills=['linked'])
        self.assertFalse(self.codex.exists())

    def test_windows_reparse_flag_is_rejected_without_host_privileges(self):
        original = Path.lstat
        def reparse(path):
            if path == self.repo:
                return SimpleNamespace(st_mode=0o40755, st_file_attributes=0x400)
            return original(path)
        with patch.object(Path, 'lstat', reparse), self.assertRaises(kit.InstallError):
            self.run_install()

    def test_symlink_flag_is_rejected_without_host_privileges(self):
        original = Path.lstat
        def symlink(path):
            if path == self.repo:
                return SimpleNamespace(st_mode=0o120777, st_file_attributes=0)
            return original(path)
        with patch.object(Path, 'lstat', symlink), self.assertRaises(kit.InstallError):
            self.run_install()


if __name__ == '__main__':
    unittest.main()
