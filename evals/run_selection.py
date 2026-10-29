"""실제 Codex 세션의 SKILL.md 읽기 증거로 선택을 평가한다. 기본은 실행 계획뿐."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
SUFFIX = """
이번 요청은 실행 전 준비 단계까지만 진행해. 현재 사용 가능한 스킬 중 작업에 적용되는 것이 있으면 그 SKILL.md를 실제로 읽고, 첫 단계만 짧게 설명해. 관계없는 스킬은 나열하지 마.
파일 수정, 스크립트 실행, 네트워크·외부 서비스 작업은 하지 마. 현재 프로젝트 자료와 선택한 스킬 문서의 읽기만 허용한다. 단순 답변이면 바로 답해.
"""
FIXTURES = {
    "README.md": "# Synthetic evaluation fixture\nPython + React example. No real users, secrets or external services.\nRun tests: python -m unittest\n",
    "package.json": '{"name":"selection-fixture","private":true,"scripts":{"test":"node --test"},"dependencies":{"react":"19.3.1","react-dom":"19.3.1","remotion":"4.0.539"}}\n',
    "codec.py": "import json\ndef encode(value): return json.dumps(value)\ndef decode(value): return json.loads(value)\n",
    "calc.py": "def divide(a, b): return a / b\n",
    "src/Search.jsx": "export function Search({rows,query}) { const found=rows.filter(r=>r.name.includes(query)).sort((a,b)=>a.name.localeCompare(b.name)); return <ul>{found.map(r=><li key={r.id}>{r.name}</li>)}</ul>\n",
    "schema.sql": "CREATE TABLE notes (id bigint PRIMARY KEY, tenant_id uuid NOT NULL, body text);\nALTER TABLE notes ENABLE ROW LEVEL SECURITY;\n",
    "captions.srt": "1\n00:00:00,300 --> 00:00:00,900\n안녕하세요\n",
    "changes.md": "# Confirmed synthetic changes\nSearch now preserves filters when paging. Added CSV export. CLI --legacy was removed; use --format plain. No deployment performed.\n",
    "progress.md": "# Progress\nImplemented search filtering. Tests pass. Remaining: keyboard focus after clearing a filter. Do not alter unrelated forms.\n",
    "candidates.md": "# Synthetic candidates\nCandidate A: code review helper, MIT, Python required. Candidate B: overlapping review helper, no license declared. No real repository URLs provided.\n",
    "changes.patch": "diff --git a/calc.py b/calc.py\n--- a/calc.py\n+++ b/calc.py\n@@ -1 +1 @@\n-def divide(a, b): return a / b\n+def divide(a, b): return None if b == 0 else a / b\n",
}


def normalize(text):
    return text.replace("\r\n", "\n").strip()


def grade(events, catalog, expected):
    observed = set()
    completed = False
    forbidden_actions = []
    usage = {}
    for event in events:
        if event.get("type") == "turn.completed":
            completed = True
            usage = event.get("usage", {})
        item = event.get("item", {})
        if event.get("type") != "item.completed":
            continue
        if item.get("type") == "command_execution" and item.get("exit_code") == 0:
            output = normalize(item.get("aggregated_output", ""))
            # Require the complete document in successful command output.
            # Final claims, names in a catalog, and failed/partial reads do not count.
            for name, content in catalog.items():
                if normalize(content) in output:
                    observed.add(name)
        if item.get("type") in {"file_change", "web_search", "mcp_tool_call"}:
            forbidden_actions.append(item.get("type"))
    missing = sorted(set(expected) - observed)
    unexpected = sorted(observed - set(expected))
    return {"passed": completed and not missing and not unexpected and not forbidden_actions,
            "expected": expected, "observed": sorted(observed), "missing": missing,
            "unexpected": unexpected, "forbidden_actions": forbidden_actions,
            "completed": completed, "usage": usage}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run",action="store_true",help="현재 Codex 로그인·기본 모델로 실제 평가 실행")
    parser.add_argument("--out",type=Path,help="개인 원시 로그용 새 폴더. 공개 저장소 밖을 권장")
    parser.add_argument("--case",action="append",default=[])
    parser.add_argument("--timeout",type=int,default=180)
    args=parser.parse_args()
    cases=json.loads((ROOT/"evals/selection-cases.json").read_text(encoding="utf-8"))
    if args.case:
        unknown=set(args.case)-{c["id"] for c in cases}
        if unknown: parser.error("unknown cases: "+str(sorted(unknown)))
        cases=[c for c in cases if c["id"] in args.case]
    if not args.run:
        print(json.dumps({"case_count":len(cases),"cases":[c["id"] for c in cases],
            "mode":"plan; no model calls; use --run --out NEW_DIRECTORY"},indent=2))
        return
    if not args.out: parser.error("--run에는 --out이 필요함")
    executable=shutil.which("codex")
    if not executable: parser.error("Codex CLI 필요")
    if not 10 <= args.timeout <= 600: parser.error("timeout must be 10..600")
    destination=args.out.expanduser().resolve()
    destination.mkdir(parents=True,exist_ok=False)
    version=subprocess.check_output([executable,"--version"],text=True,encoding="utf-8").strip()
    catalog={p.parent.name:p.read_text(encoding="utf-8") for p in sorted((ROOT/"skills").glob("*/SKILL.md"))}
    results=[]
    for case in cases:
        case_root=destination/case["id"]
        fixture=case_root/"project"; fixture.mkdir(parents=True)
        for name,content in FIXTURES.items():
            file=fixture/name; file.parent.mkdir(parents=True,exist_ok=True)
            file.write_text(content,encoding="utf-8")
        before={str(p.relative_to(fixture)):hashlib.sha256(p.read_bytes()).hexdigest() for p in fixture.rglob("*") if p.is_file()}
        command=[executable,"exec","--ephemeral","--json","--sandbox","read-only",
            "--skip-git-repo-check","-C",str(fixture),"-"]
        started=time.monotonic()
        print("START "+case["id"],flush=True)
        try:
            proc=subprocess.run(command,input=case["prompt"]+"\n"+SUFFIX,
                text=True,encoding="utf-8",capture_output=True,timeout=args.timeout)
            raw,error,code=proc.stdout,proc.stderr,proc.returncode
        except subprocess.TimeoutExpired as exc:
            raw=exc.stdout or b""; error=exc.stderr or b""
            raw=raw.decode("utf-8",errors="replace") if isinstance(raw,bytes) else raw
            error=error.decode("utf-8",errors="replace") if isinstance(error,bytes) else error
            code=124
        (case_root/"trace.jsonl").write_text(raw,encoding="utf-8")
        (case_root/"stderr.txt").write_text(error,encoding="utf-8")
        events=[]; malformed=False
        for line in raw.splitlines():
            try: events.append(json.loads(line))
            except ValueError: malformed=True
        result=grade(events,catalog,case["expected"])
        after={str(p.relative_to(fixture)):hashlib.sha256(p.read_bytes()).hexdigest() for p in fixture.rglob("*") if p.is_file()}
        result.update(id=case["id"],kind=case["kind"],exit_code=code,
            fixture_unchanged=before==after,trace_sha256=hashlib.sha256(raw.encode()).hexdigest(),
            elapsed_seconds=round(time.monotonic()-started,2))
        result["passed"] &= code==0 and not malformed and before==after
        results.append(result)
        print(("PASS " if result["passed"] else "FAIL ")+case["id"]+" "+json.dumps({k:result[k] for k in ("observed","missing","unexpected")}),flush=True)
        summary={"cli_version":version,"model":"current user default; no model override",
            "scope":"native skill selection under a read-only preparation request; kit skills only",
            "case_count":len(results),"passed":sum(r["passed"] for r in results),"results":results,
            "skill_sha256":{n:hashlib.sha256(c.encode()).hexdigest() for n,c in catalog.items()}}
        (destination/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
    raise SystemExit(0 if all(r["passed"] for r in results) else 1)


if __name__=="__main__":
    main()
