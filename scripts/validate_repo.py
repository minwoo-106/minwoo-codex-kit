"""배포 문서·스킬·프로필·잠금 파일을 검증한다. 외부 패키지나 모델 호출 없음."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import subprocess
from profiles import load_profiles

ROOT=Path(__file__).absolute().parent.parent
GENERATED={".git","node_modules","__pycache__",".pytest_cache",".hypothesis",".venv","work",".minwoo-codex-kit"}
SECRET_PATTERNS=[re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{30,}"),
                 re.compile(r"\bgithub_pat_[A-Za-z0-9_]{50,}"),
                 re.compile(r"\bsk-proj-[A-Za-z0-9_-]{30,}"),
                 re.compile(r"\bAKIA[0-9A-Z]{16}\b")]


def metadata(path):
    text=path.read_text(encoding="utf-8")
    if not text.startswith("---\n"): raise ValueError(str(path)+": missing frontmatter")
    parts=text.split("---",2)
    if len(parts)!=3: raise ValueError("unterminated frontmatter")
    fields={}
    for line in parts[1].splitlines():
        match=re.match(r"^(name|description):\s*(.+)$",line)
        if match: fields[match[1]]=match[2].strip().strip("'\"")
    if fields.get("name")!=path.parent.name: raise ValueError(str(path)+": name mismatch")
    if not fields.get("description") or len(fields["description"])>1024:
        raise ValueError(str(path)+": missing/oversized one-line description")
    if re.search(r"\[TODO|TODO:",text): raise ValueError(str(path)+": unfinished scaffold")
    return fields


def validate(root=ROOT):
    errors=[]
    skills=sorted((root/"skills").glob("*/SKILL.md"))
    names={p.parent.name for p in skills}
    for skill in skills:
        try: metadata(skill)
        except (ValueError,UnicodeError) as exc: errors.append(str(exc))
    try:
        profiles=load_profiles(root)
        if set(profiles["all"]["skills"])!=names: errors.append("all profile must match distributed skills")
    except (OSError,ValueError,KeyError,TypeError) as exc: errors.append("profiles: "+str(exc))
    cases=json.loads((root/"evals/selection-cases.json").read_text(encoding="utf-8"))
    if len({c["id"] for c in cases})!=len(cases): errors.append("duplicate eval IDs")
    if not any(not c["expected"] for c in cases): errors.append("missing negative evals")
    covered=set()
    for case in cases:
        if set(case["expected"])-names: errors.append("unknown expected skill: "+case["id"])
        if not case.get("prompt"): errors.append("empty eval prompt: "+case["id"])
        covered.update(case["expected"])
    if covered!=names: errors.append("selection eval coverage does not include every kit skill")
    package=json.loads((root/"tooling/package.json").read_text(encoding="utf-8"))
    lock=json.loads((root/"tooling/package-lock.json").read_text(encoding="utf-8"))
    if lock["packages"][""]["dependencies"]!=package["dependencies"]: errors.append("Node lock/manifest mismatch")
    for line in (root/"tooling/requirements.txt").read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.startswith("#") and not re.match(r"[A-Za-z0-9_.-]+==[^\s;]+.*--hash=sha256:[a-f0-9]{64}",line):
            errors.append("Python requirement is not version/hash pinned")
    upstream=json.loads((root/"docs/upstream-files.json").read_text(encoding="utf-8"))
    for entry in upstream["files"]:
        path=root/entry["local"]
        if not path.is_file(): errors.append("missing vendored resource: "+entry["local"])
        skill_root=root/"/".join(Path(entry["local"]).parts[:2])
        if not (skill_root/"LICENSE").is_file() or not (skill_root/"UPSTREAM.md").is_file():
            errors.append("missing license/provenance: "+entry["local"])
    try:
        proc=subprocess.run(["git","ls-files","--cached","--others","--exclude-standard","-z"],cwd=root,capture_output=True,check=True)
        files=[root/name for name in proc.stdout.decode().split("\0") if name]
    except (OSError,subprocess.SubprocessError):
        files=[p for p in root.rglob("*") if p.is_file() and not GENERATED.intersection(p.relative_to(root).parts)]
    for path in files:
        relative=path.relative_to(root)
        if GENERATED.intersection(relative.parts): errors.append("generated file in distribution: "+str(relative)); continue
        if path.name in {"auth.json","config.toml",".env"} or path.suffix in {".pem",".pfx",".p12",".key",".pyc",".pyo"}:
            errors.append("private/generated file: "+str(relative)); continue
        try: text=path.read_text(encoding="utf-8")
        except (UnicodeError,OSError): errors.append("non-text/missing source: "+str(relative)); continue
        if any(pattern.search(text) for pattern in SECRET_PATTERNS):
            errors.append("possible credential: "+str(relative))
        if str(Path.home()).replace("\\","/").lower() in text.replace("\\","/").lower():
            errors.append("personal absolute path: "+str(relative))
        if path.suffix==".md":
            for link in re.findall(r"\]\(([^)]+)\)",text):
                if link.startswith(("http:","https:","mailto:","#")) or any(c in link for c in (" ","<","{")): continue
                if not (path.parent/link.split("#")[0]).exists(): errors.append("broken link: "+str(relative)+" -> "+link)
    return {"skills":len(skills),"selection_cases":len(cases),"files":len(files),"errors":errors}


if __name__=="__main__":
    result=validate()
    print(json.dumps(result,ensure_ascii=False,indent=2))
    raise SystemExit(bool(result["errors"]))
