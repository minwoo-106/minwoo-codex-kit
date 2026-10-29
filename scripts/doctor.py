"""kit의 설치·도구 상태를 읽기 전용으로 점검한다. 기본 출력에서 개인 경로를 숨긴다."""
from __future__ import annotations
import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from profiles import load_profiles
from install import check_path

ROOT=Path(__file__).absolute().parent.parent
spec=importlib.util.spec_from_file_location("kit_inspect",ROOT/"skills/minwoo-kit-maintenance/scripts/inspect_kit.py")
inspection=importlib.util.module_from_spec(spec); spec.loader.exec_module(inspection)
spec2=importlib.util.spec_from_file_location("kit_tools",ROOT/"scripts/setup-tools.py")
setup=importlib.util.module_from_spec(spec2); spec2.loader.exec_module(setup)


def probe(command):
    executable=shutil.which(command)
    if not executable: return {"available":False}
    if command=="codex":
        # codex --version can create its own temp aliases. Do not invoke it in a read-only doctor.
        return {"available":True,"execution_checked":False}
    try:
        p=subprocess.run([executable,"--version"],capture_output=True,text=True,
                         encoding="utf-8",errors="replace",timeout=10)
        return {"available":True,"execution_checked":p.returncode==0,"version":p.stdout.strip().splitlines()[0] if p.stdout.strip() else None}
    except (OSError,subprocess.SubprocessError):
        return {"available":True,"execution_checked":False}


def inspect_environment(repo, codex_home, roots, profile):
    expected=set(load_profiles(repo)[profile]["skills"])
    report=inspection.inspect(repo,codex_home,roots)
    skills=[]
    warnings=[]
    for name in sorted(expected):
        copies=[x for x in report["skills"] if x["skill"]==name and x["installed"]]
        state="missing" if not copies else "same"
        if len(copies)>1: state="duplicate"
        elif copies and any(copies[0][key] for key in ("different","missing","extra")): state="different"
        skills.append({"name":name,"status":state})
        if state!="same": warnings.append(name+": "+state)
    tools={name:probe(name) for name in ("git","node","codex")}
    tools["python"]={"available":True,"version":".".join(map(str,sys.version_info[:3])),
                     "base_supported":sys.version_info>=(3,10),"optional_supported":sys.version_info>=(3,11)}
    browsers=[shutil.which(x) for x in ("google-chrome","chromium","chromium-browser","msedge")]
    browsers += [os.path.join(os.environ.get("PROGRAMFILES(X86)",""),"Microsoft/Edge/Application/msedge.exe"),
                 os.path.join(os.environ.get("PROGRAMFILES",""),"Google/Chrome/Application/chrome.exe"),
                 "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"]
    browser_found=any(p and Path(p).is_file() for p in browsers)
    runtimes=[]
    runtime_root=codex_home/".minwoo-codex-kit/runtimes"
    check_path(runtime_root)
    hashes=setup.file_hashes(setup.source_files())
    if runtime_root.is_dir():
        for candidate in sorted(runtime_root.iterdir()):
            check_path(candidate)
            if not candidate.is_dir(): continue
            receipt=candidate/"installed.json"; check_path(receipt)
            if not receipt.is_file():
                runtimes.append({"id":candidate.name,"status":"incomplete"}); continue
            try:
                setup.verify_existing(candidate,hashes)
                setup.check_runtime_files(candidate)
                status="ready"
            except (OSError,ValueError,KeyError,setup.InstallError):
                status="different-or-incomplete"
            runtimes.append({"id":candidate.name,"status":status})
    for name in ("git","node"):
        if not tools[name]["available"]: warnings.append(name+": unavailable")
    if tools["node"].get("version"):
        try:
            if int(tools["node"]["version"].lstrip("v").split(".")[0])<22:
                warnings.append("node: optional tools need 22+")
        except ValueError: warnings.append("node: unrecognized version")
    if not any(x["status"]=="ready" for x in runtimes): warnings.append("optional runtime: unavailable or changed")
    if not browser_found: warnings.append("browser: not detected (not a render test)")
    return {"profile":profile,"skills":skills,"rules":report["rules"]["status"],
            "override_present":report["rules"]["override_present"],
            "duplicates":sorted(report["duplicates"]),"tools":tools,
            "browser":{"detected":browser_found,"execution_checked":False},"runtimes":runtimes,
            "warnings":warnings,"plugin_connections":"not tested; skill files do not prove account access",
            "read_only":True}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex-home",type=Path,default=Path(os.environ.get("CODEX_HOME",str(Path.home()/".codex"))))
    parser.add_argument("--skills-root",type=Path,action="append")
    parser.add_argument("--profile",choices=list(load_profiles(ROOT)),default="all")
    parser.add_argument("--json",action="store_true")
    args=parser.parse_args()
    roots=args.skills_root or [Path.home()/".agents/skills",args.codex_home/"skills"]
    try: result=inspect_environment(ROOT,args.codex_home,roots,args.profile)
    except (OSError,ValueError,setup.InstallError) as exc:
        print(json.dumps({"error":type(exc).__name__,"message":"점검을 완료하지 못함. 경로·파일 형식을 로컬에서 확인할 것."},ensure_ascii=False))
        return 1
    if args.json: print(json.dumps(result,ensure_ascii=False,indent=2))
    else:
        print("Skills: "+", ".join(x["name"]+"="+x["status"] for x in result["skills"]))
        print("Rules: "+result["rules"]+" (차이는 자동 수정 대상이 아님)")
        print("Tools: "+json.dumps(result["tools"],ensure_ascii=False))
        print("Runtime: "+json.dumps(result["runtimes"],ensure_ascii=False))
        for warning in result["warnings"]: print("CHECK "+warning)
        print("읽기 전용 점검 완료. 계정 연결·실제 렌더 동작은 별도 검증.")
    return 0


if __name__=="__main__": raise SystemExit(main())
