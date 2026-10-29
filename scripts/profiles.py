"""명시적으로 선택한 설치 묶음만 확장한다. 설정·설치는 수행하지 않는다."""
import json
from pathlib import Path
import re


def load_profiles(repo: Path) -> dict:
    data=json.loads((repo/"profiles.json").read_text(encoding="utf-8"))
    if data.get("schema")!=1 or not isinstance(data.get("profiles"),dict):
        raise ValueError("지원하지 않는 설치 묶음 형식")
    for name,entry in data["profiles"].items():
        if not re.fullmatch(r"[a-z][a-z0-9-]*",name) or not isinstance(entry,dict):
            raise ValueError("잘못된 설치 묶음 이름")
        skills=entry.get("skills")
        if not isinstance(skills,list) or not skills or not all(isinstance(s,str) for s in skills) or len(skills)!=len(set(skills)):
            raise ValueError("비어 있거나 중복된 스킬 묶음: "+name)
        if not isinstance(entry.get("description"),str) or not entry["description"].strip():
            raise ValueError("묶음 설명 누락: "+name)
        for skill in skills:
            if not isinstance(skill,str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*",skill):
                raise ValueError("잘못된 스킬 이름")
            if not (repo/"skills"/skill/"SKILL.md").is_file():
                raise ValueError("묶음에 없는 스킬이 포함됨: "+skill)
    return data["profiles"]


def expand(repo: Path, names: list[str], skills: list[str]) -> list[str]:
    profiles=load_profiles(repo)
    result=set(skills)
    for name in names:
        if name not in profiles:
            raise ValueError("찾을 수 없는 설치 묶음: "+name)
        result.update(profiles[name]["skills"])
    return sorted(result)
