#!/usr/bin/env python3
"""Codex 실행 설정을 유지하면서 선택한 규칙과 스킬을 설치한다."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import tempfile
import uuid
from dataclasses import dataclass

REPO = Path(__file__).absolute().parent.parent
STATE_DIR = '.minwoo-codex-kit'
GENERATED_DIRS = {'__pycache__', '.pytest_cache', '.hypothesis', 'node_modules', '.venv'}


class InstallError(Exception):
    pass


def absolute(path: str | Path) -> Path:
    return Path(os.path.abspath(os.path.expanduser(str(path))))


def check_path(path: Path) -> None:
    """resolve()가 경로 이탈을 숨기지 않도록 원래 경로의 링크부터 검사한다."""
    for part in reversed((path, *path.parents)):
        try:
            info = part.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400:
            raise InstallError(f'링크·정션·reparse point 경로는 사용할 수 없음: {part}')


def within(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_file(path: Path) -> bytes | None:
    check_path(path)
    if not path.exists():
        return None
    if not path.is_file():
        raise InstallError(f'일반 파일이 필요한 위치임: {path}')
    return path.read_bytes()


def atomic_write(path: Path, data: bytes, mode: int = 0o600) -> None:
    check_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix='.kit-', suffix='.tmp', dir=path.parent)
    temp = Path(name)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        temp.chmod(mode)
        check_path(path)
        os.replace(temp, path)
    finally:
        if temp.exists():
            temp.unlink()


@dataclass
class Change:
    target: Path
    content: bytes
    before: bytes | None
    mode: int


def sources(repo: Path, skills: list[str], include_rules: bool, project: bool):
    result = []
    if include_rules:
        result.append((repo / ('templates' if project else 'global') / 'AGENTS.md', 'rules', Path('AGENTS.md')))
    for name in sorted(set(skills)):
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name) or len(name) > 64:
            raise InstallError(f'잘못된 스킬 이름: {name}')
        root = repo / 'skills' / name
        check_path(root)
        if not (root / 'SKILL.md').is_file():
            raise InstallError(f'찾을 수 없는 스킬: {name}')
        for item in skill_files(root):
            result.append((item, 'skills', Path(name) / item.relative_to(root)))
    if not result:
        raise InstallError('설치 대상이 없음. 규칙 또는 --skill을 선택할 것.')
    return result


def skill_files(root: Path):
    for item in sorted(root.iterdir()):
        check_path(item)
        if item.is_dir():
            if item.name in GENERATED_DIRS:
                continue
            yield from skill_files(item)
        elif item.is_file():
            if item.suffix in {'.pyc', '.pyo'}:
                continue
            yield item
        else:
            raise InstallError(f'지원하지 않는 원본 파일: {item}')


def load_state(raw: bytes | None) -> dict:
    if raw is None:
        return {'schema': 1, 'files': {}}
    try:
        state = json.loads(raw)
        if state['schema'] != 1 or not isinstance(state['files'], dict):
            raise ValueError()
        for key, value in state['files'].items():
            if not isinstance(key, str) or not isinstance(value, str) or not re.fullmatch('[0-9a-f]{64}', value):
                raise ValueError()
        return state
    except (ValueError, KeyError, TypeError) as exc:
        raise InstallError('설치 상태 파일이 올바르지 않음. 보존하고 내용을 확인한 뒤 재시도할 것.') from exc


def plan_install(repo: Path, roots: dict, selected, state_path: Path, replace: bool, report=True):
    raw_state = read_file(state_path)
    state = load_state(raw_state)
    changes, conflicts = [], []
    files = dict(state['files'])
    for source, kind, relative in selected:
        data = read_file(source)
        if data is None:
            raise InstallError(f'원본 파일이 없음: {source}')
        target = roots[kind] / relative
        key = os.path.normcase(str(target))
        before = read_file(target)
        if before == data:
            if report:
                print(f'변경 없음: {target}')
        elif before is not None and files.get(key) != digest(before) and not replace:
            conflicts.append(target)
        else:
            mode = stat.S_IMODE(target.stat().st_mode if before is not None else source.stat().st_mode)
            changes.append(Change(target, data, before, mode))
        files[key] = digest(data)
    if conflicts:
        names = '\n'.join(str(p) for p in conflicts)
        raise InstallError('기존 파일 또는 로컬 수정과 충돌해 설치를 중단함:\n' + names +
                           '\n차이를 먼저 확인할 것. --replace-existing을 지정하면 백업 후 교체함.')
    version = read_file(repo / 'VERSION')
    if version is None:
        raise InstallError('VERSION 파일이 없음.')
    next_state = {'schema': 1, 'version': version.decode('utf-8').strip(), 'files': files}
    state_data = (json.dumps(next_state, ensure_ascii=False, indent=2, sort_keys=True) + '\n').encode('utf-8')
    if state_data != raw_state:
        changes.append(Change(state_path, state_data, raw_state, 0o600))
    return changes


def install(repo: Path, *, scope='user', project=None, codex_home=None, skills_root=None,
            skills=(), skip_rules=False, dry_run=False, replace_existing=False) -> int:
    repo = absolute(repo)
    check_path(repo)
    if scope == 'project':
        if not project or codex_home or skills_root:
            raise InstallError('프로젝트 설치에는 --project가 필요하고 --codex-home/--skills-root는 사용할 수 없음.')
        base = absolute(project)
        if not base.is_dir():
            raise InstallError('프로젝트 폴더가 먼저 존재해야 함.')
        roots = {'rules': base, 'skills': base / '.agents' / 'skills'}
    else:
        if project:
            raise InstallError('--project에는 --scope project가 필요함.')
        base = absolute(codex_home or os.environ.get('CODEX_HOME') or Path.home() / '.codex')
        roots = {'rules': base, 'skills': absolute(skills_root or Path.home() / '.agents' / 'skills')}
    for root in roots.values():
        check_path(root)
        if root.exists() and not root.is_dir():
            raise InstallError(f'폴더가 필요한 위치임: {root}')
        if within(root, repo) or within(repo, root):
            raise InstallError('설치 대상과 kit 원본 저장소 경로는 중첩될 수 없음.')
    if not skip_rules:
        override = roots['rules'] / 'AGENTS.override.md'
        if override.exists():
            print(f'주의: {override} 파일이 설치된 AGENTS.md보다 우선 적용될 수 있음.')
    selected = sources(repo, list(skills), not skip_rules, scope == 'project')
    state_folder = base / STATE_DIR
    check_path(state_folder)
    state_path = state_folder / 'state.json'
    # 폴더나 잠금을 만들기 전에 전체 대상의 충돌을 먼저 확인한다.
    changes = plan_install(repo, roots, selected, state_path, replace_existing)
    if dry_run:
        for change in changes:
            print(f'{"교체 예정" if change.before is not None else "생성 예정"}: {change.target}')
        print(f'미리보기: 변경 예정 {len(changes)}개, 파일 쓰기 없음.')
        return 0
    if not changes:
        print('설치본이 원본과 같음. 파일 쓰기 없음.')
        return 0
    state_folder.mkdir(parents=True, exist_ok=True, mode=0o700)
    lock = state_folder / 'install.lock'
    check_path(lock)
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise InstallError(f'설치 잠금이 있음: {lock}. 삭제 전 다른 설치기가 실행 중인지 확인할 것.') from exc
    os.close(fd)
    applied = []
    backup = None
    try:
        changes = plan_install(repo, roots, selected, state_path, replace_existing, report=False)
        old = [change for change in changes if change.before is not None]
        if old:
            backup = state_folder / 'backups' / uuid.uuid4().hex
            backup.mkdir(parents=True, mode=0o700)
            mapping = []
            for index, change in enumerate(old):
                name = f'{index:04d}.bak'
                atomic_write(backup / name, change.before)
                mapping.append({'backup': name, 'target': str(change.target), 'mode': change.mode})
            atomic_write(backup / 'restore-map.json', (json.dumps(mapping, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
            print(f'백업: {backup}')
        for change in changes:
            if read_file(change.target) != change.before:
                raise InstallError(f'설치 도중 파일이 변경됨: {change.target}')
            atomic_write(change.target, change.content, change.mode)
            applied.append(change)
            print(f'기록: {change.target}')
    except BaseException:
        failures = []
        for change in reversed(applied):
            try:
                if read_file(change.target) != change.content:
                    raise InstallError('다른 편집이 감지되어 자동 복구를 생략함')
                if change.before is None:
                    change.target.unlink()
                else:
                    atomic_write(change.target, change.before, change.mode)
            except (OSError, InstallError) as exc:
                failures.append(f'{change.target}: {exc}')
        if failures:
            print('수동 복구 확인이 필요함:\n' + '\n'.join(failures), file=sys.stderr)
        if backup:
            print(f'백업 보존 위치: {backup}', file=sys.stderr)
        raise
    finally:
        lock.unlink()
    print('설치 완료. 실행 설정은 유지됨. 변경이 보이지 않으면 Codex를 재시작할 것.')
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scope', choices=['user', 'project'], default='user')
    parser.add_argument('--project')
    parser.add_argument('--codex-home')
    parser.add_argument('--skills-root')
    parser.add_argument('--skill', action='append', dest='skills', default=[])
    parser.add_argument('--profile', action='append', dest='profiles', default=[])
    parser.add_argument('--list-profiles', action='store_true')
    parser.add_argument('--skip-rules', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--replace-existing', action='store_true')
    args = parser.parse_args()
    try:
        from profiles import load_profiles, expand
        if args.list_profiles:
            for name, entry in load_profiles(REPO).items():
                print(f"{name}: {entry['description']} ({len(entry['skills'])} skills)")
            return 0
        del args.list_profiles
        selected_profiles = args.profiles
        del args.profiles
        if selected_profiles:
            args.skills = expand(REPO, selected_profiles, args.skills)
        return install(REPO, **vars(args))
    except (OSError, ValueError, InstallError) as exc:
        print(f'오류: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    if sys.version_info < (3, 10):
        sys.exit('Python 3.10 이상이 필요함.')
    sys.exit(main())
