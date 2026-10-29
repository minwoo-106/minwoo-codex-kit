"""실제 배포 파일을 Python 및 사용 가능한 셸 진입점으로 검증한다."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
SKILL = 'minwoo-project-context'


class EntrypointTests(unittest.TestCase):
    def setUp(self):
        test_dir = os.environ.get('KIT_TEST_ROOT')
        self.temp = tempfile.TemporaryDirectory(prefix='entry-', dir=os.path.abspath(test_dir) if test_dir else None)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.codex = self.root / '개인 규칙'
        self.skills = self.root / '선택 스킬'
        self.env = dict(os.environ, PYTHONIOENCODING='utf-8', PYTHONDONTWRITEBYTECODE='1')

    def execute(self, args):
        return subprocess.run(args, cwd=self.root, env=self.env, capture_output=True, encoding='utf-8', errors='replace')

    def invoke(self, args, expected=0):
        proc = self.execute(args)
        self.assertEqual(proc.returncode, expected, proc.stdout + proc.stderr)
        return proc

    def verify_installed(self):
        self.assertEqual((self.codex / 'AGENTS.md').read_bytes(), (REPO / 'global' / 'AGENTS.md').read_bytes())
        self.assertEqual((self.skills / SKILL / 'SKILL.md').read_bytes(), (REPO / 'skills' / SKILL / 'SKILL.md').read_bytes())
        self.assertFalse((self.skills / 'minwoo-publication-review').exists())
        json.loads((self.codex / '.minwoo-codex-kit' / 'state.json').read_text(encoding='utf-8'))

    def python_args(self):
        return [sys.executable, str(REPO / 'scripts' / 'install.py'), '--codex-home', str(self.codex),
                '--skills-root', str(self.skills), '--skill', SKILL]

    def test_python_cli_and_repeat(self):
        self.invoke(self.python_args())
        self.verify_installed()
        result = self.invoke(self.python_args())
        self.assertIn('파일 쓰기 없음', result.stdout)

    def test_python_cli_conflict_reports_failure(self):
        self.codex.mkdir()
        (self.codex / 'AGENTS.md').write_bytes(b'keep my rule')
        self.invoke(self.python_args(), expected=1)
        self.assertEqual((self.codex / 'AGENTS.md').read_bytes(), b'keep my rule')
        self.assertFalse(self.skills.exists())

    def test_python_dry_run_has_no_side_effects(self):
        self.invoke(self.python_args() + ['--dry-run'])
        self.assertFalse(self.codex.exists())
        self.assertFalse(self.skills.exists())

    def test_four_new_skills_include_resources_and_preserve_existing_rules(self):
        names = ["minwoo-skill-curation", "minwoo-work-handoff",
                 "minwoo-kit-maintenance", "minwoo-video-review"]
        self.codex.mkdir()
        (self.codex / "AGENTS.md").write_bytes(b"keep local rules")
        existing = self.skills / "studio-review" / "SKILL.md"
        existing.parent.mkdir(parents=True)
        existing.write_bytes(b"keep project-specific skill")
        args = [sys.executable, str(REPO / "scripts/install.py"), "--skip-rules",
                "--codex-home", str(self.codex), "--skills-root", str(self.skills)]
        for name in names:
            args += ["--skill", name]
        self.invoke(args + ["--dry-run"])
        self.assertFalse((self.skills / names[0]).exists())
        self.invoke(args)
        for name in names:
            for original in (REPO / "skills" / name).rglob("*"):
                if original.is_file():
                    installed = self.skills / name / original.relative_to(REPO / "skills" / name)
                    self.assertEqual(installed.read_bytes(), original.read_bytes())
        self.assertEqual((self.codex / "AGENTS.md").read_bytes(), b"keep local rules")
        self.assertEqual(existing.read_bytes(), b"keep project-specific skill")
        self.assertIn("파일 쓰기 없음", self.invoke(args).stdout)

    def check_powershell(self, binary):
        shell = shutil.which(binary)
        if not shell:
            self.skipTest(f'{binary} not available')
        args = [shell, '-NoProfile', '-File', str(REPO / 'scripts' / 'install.ps1'),
                '-CodexHome', str(self.codex), '-SkillsRoot', str(self.skills), '-Skills', SKILL]
        first = self.execute(args + ['-DryRun'])
        if first.returncode and 'UnauthorizedAccess' in first.stderr and 'running scripts is disabled' in first.stderr:
            self.skipTest('Host execution policy blocks .ps1 files; policy left unchanged')
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        self.assertFalse(self.codex.exists())
        self.invoke(args)
        self.verify_installed()
        self.invoke(args)
        (self.codex / 'AGENTS.md').write_bytes(b'edited after install')
        self.invoke(args, expected=1)
        self.assertEqual((self.codex / 'AGENTS.md').read_bytes(), b'edited after install')

    def test_powershell_7_wrapper(self):
        self.check_powershell('pwsh')

    def test_powershell_7_multiple_skill_arguments(self):
        shell = shutil.which('pwsh')
        if not shell:
            self.skipTest('pwsh not available')
        self.env.update(KIT_SCRIPT_PATH=str(REPO / 'scripts' / 'install.ps1'),
                        KIT_RULES_PATH=str(self.codex), KIT_SKILLS_PATH=str(self.skills))
        code = ('& $env:KIT_SCRIPT_PATH -CodexHome $env:KIT_RULES_PATH -SkillsRoot $env:KIT_SKILLS_PATH '
                '-Skills minwoo-project-context,minwoo-publication-review')
        self.invoke([shell, '-NoProfile', '-Command', code])
        for name in (SKILL, 'minwoo-publication-review'):
            self.assertTrue((self.skills / name / 'SKILL.md').is_file())

    def test_windows_powershell_51_wrapper(self):
        self.check_powershell('powershell')

    def test_windows_powershell_51_syntax(self):
        shell = shutil.which('powershell')
        if not shell:
            self.skipTest('Windows PowerShell not available')
        self.env['KIT_SCRIPT_PATH'] = str(REPO / 'scripts' / 'install.ps1')
        code = ('$tokens=$null; $errors=$null; '
                '[void][System.Management.Automation.Language.Parser]::ParseFile('
                '$env:KIT_SCRIPT_PATH,[ref]$tokens,[ref]$errors); '
                'if ($errors.Count) { $errors | Out-String | Write-Output; exit 1 }; exit 0')
        self.invoke([shell, '-NoProfile', '-Command', code])

    def test_sh_wrapper(self):
        if os.name == 'nt':
            shell = Path(os.environ.get('ProgramFiles', 'C:/Program Files')) / 'Git' / 'bin' / 'sh.exe'
            if not shell.is_file():
                self.skipTest('Git for Windows sh not available')
        else:
            shell = shutil.which('sh')
            if not shell:
                self.skipTest('sh not available')
        args = [str(shell), str(REPO / 'scripts' / 'install.sh'), '--codex-home', str(self.codex),
                '--skills-root', str(self.skills), '--skill', SKILL]
        self.invoke(args + ['--dry-run'])
        self.assertFalse(self.codex.exists())
        self.invoke(args)
        self.verify_installed()
        self.invoke(args)


if __name__ == '__main__':
    unittest.main()
