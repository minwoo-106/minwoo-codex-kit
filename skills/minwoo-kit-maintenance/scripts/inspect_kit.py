"""kit 관리 대상만 읽어 비교한다. 설치·삭제·원격 접속은 하지 않는다."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import sys

GENERATED_DIRS = {"__pycache__", ".pytest_cache", ".hypothesis", "node_modules", ".venv"}


def checked(path: Path) -> Path:
    path = Path(os.path.abspath(path.expanduser()))
    for part in (path, *path.parents):
        try:
            info = part.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise ValueError(f"링크·정션 경로를 확인해야 함: {part}")
    return path


def files(root: Path) -> dict[str, str]:
    checked(root)
    result = {}
    if not root.exists():
        return result
    if not root.is_dir():
        raise ValueError(f"폴더가 아닌 경로: {root}")
    for item in sorted(root.iterdir()):
        checked(item)
        if item.is_dir():
            if item.name in GENERATED_DIRS:
                continue
            for name, value in files(item).items():
                result[f"{item.name}/{name}"] = value
        elif item.is_file():
            if item.suffix in {".pyc", ".pyo"}:
                continue
            result[item.name] = hashlib.sha256(item.read_bytes()).hexdigest()
        else:
            raise ValueError(f"일반 파일이 아닌 항목: {item}")
    return result


def compare(source: dict[str, str], installed: dict[str, str]) -> dict:
    return {
        "same": sorted(k for k in source.keys() & installed.keys() if source[k] == installed[k]),
        "different": sorted(k for k in source.keys() & installed.keys() if source[k] != installed[k]),
        "missing": sorted(source.keys() - installed.keys()),
        "extra": sorted(installed.keys() - source.keys()),
    }


def inspect(kit: Path, codex_home: Path, roots: list[Path]) -> dict:
    kit, codex_home = checked(kit), checked(codex_home)
    roots = list(dict.fromkeys(checked(p) for p in roots))
    source_rules = checked(kit / "global" / "AGENTS.md")
    if not source_rules.is_file() or not checked(kit / "skills").is_dir():
        raise ValueError("global/AGENTS.md와 skills가 있는 kit 경로가 필요함")
    local_rules = checked(codex_home / "AGENTS.md")
    rule_state = "absent"
    if local_rules.exists():
        if not local_rules.is_file():
            raise ValueError("전역 AGENTS.md가 일반 파일이 아님")
        rule_state = "same" if source_rules.read_bytes() == local_rules.read_bytes() else "different"
    inventory = {}
    for root in roots:
        if not root.exists():
            continue
        if not root.is_dir():
            raise ValueError(f"스킬 폴더가 아님: {root}")
        for child in sorted(root.iterdir()):
            checked(child)
            if child.name.startswith(".") or not child.is_dir():
                continue
            entry = checked(child / "SKILL.md")
            if entry.is_file():
                inventory.setdefault(child.name, []).append(str(child))
    managed = []
    for skill in sorted((kit / "skills").iterdir()):
        checked(skill)
        if not skill.is_dir() or not checked(skill / "SKILL.md").is_file():
            continue
        source = files(skill)
        for root in roots:
            target = checked(root / skill.name)
            managed.append({
                "skill": skill.name, "path": str(target),
                "installed": target.exists(),
                **compare(source, files(target)),
            })
    return {
        "rules": {"path": str(local_rules), "status": rule_state,
                  "override_present": checked(codex_home / "AGENTS.override.md").exists()},
        "skills": managed,
        "duplicates": {name: paths for name, paths in inventory.items() if len(paths) > 1},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kit", type=Path, required=True)
    parser.add_argument("--codex-home", type=Path,
                        default=Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")))
    parser.add_argument("--skills-root", type=Path, action="append")
    args = parser.parse_args()
    try:
        roots = args.skills_root or [Path.home() / ".agents" / "skills", args.codex_home / "skills"]
        print(json.dumps(inspect(args.kit, args.codex_home, roots), ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError) as exc:
        print(f"점검 실패: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
