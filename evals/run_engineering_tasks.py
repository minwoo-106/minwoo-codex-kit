"""Native skill implementation tasks, checked by a separate deterministic verifier."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
from engineering_fixtures import CASES, setup, verify, npm_command

ROOT=Path(__file__).resolve().parents[1]


def write(path,value):
    path.write_text(value if isinstance(value,str) else json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',action='store_true');parser.add_argument('--out',type=Path)
    parser.add_argument('--case',action='append',choices=list(CASES))
    parser.add_argument('--verify',type=Path);parser.add_argument('--verify-case',choices=list(CASES))
    args=parser.parse_args()
    if args.verify:
        if not args.verify_case:parser.error('--verify-case required')
        try:checks=verify(args.verify.resolve(),args.verify_case)
        except Exception as exc:checks=[{'name':'verifier exception','passed':False,'error_type':type(exc).__name__}]
        print(json.dumps({'passed':bool(checks) and all(c['passed'] for c in checks),'checks':checks}));return
    cases=args.case or list(CASES)
    if not args.run:print(json.dumps({'cases':cases,'mode':'plan; no model calls'}));return
    exe=shutil.which('codex')
    if not exe or not args.out:parser.error('Codex and --out required')
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);results=[]
    for case in cases:
        folder=out/case;folder.mkdir()
        try:setup(folder,case)
        except (OSError,RuntimeError,subprocess.SubprocessError) as exc:
            result=dict(case=case,passed=False,phase='fixture setup',error_type=type(exc).__name__)
            results.append(result);write(out/'summary.json',dict(cases=len(results),passed=sum(r['passed'] for r in results),results=results))
            print(json.dumps(result),flush=True);continue
        name,task=CASES[case]
        skill=ROOT/'skills'/name/'SKILL.md'
        if not skill.exists():skill=Path.home()/'.codex/skills'/name/'SKILL.md'
        documents=[skill]
        refs={'contract':ROOT/'skills/minwoo-api-compat/references/consumer-contracts.md',
              'flaky':ROOT/'skills/diagnosing-bugs/references/flaky-tests.md',
              'refactor':ROOT/'skills/minwoo-skill-curation/references/routing/refactoring.md'}
        if case in refs:documents.append(refs[case])
        protected=[folder/'README.md']
        if case=='upgrade':protected += [folder/'MIGRATION.md',*sorted((folder/'vendor').glob('*'))]
        if case=='contract':protected.append(folder/'consumer.py')
        if case=='quality':protected.append(folder/'app.py')
        before={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
        prompt=f'Use ${name} at {skill}.\n'+''.join(f'작업에 필요한 참고: {p}\n' for p in documents[1:])+task+'\n이 폴더는 합성 시험 프로젝트다. 실제 구현과 관련 실행 검증을 마쳐줘. 기존 승인·전역 설정을 변경하지 마. 외부 서비스·웹 검색·패키지 registry 접속·MCP·추가 에이전트 호출은 하지 마. 제공된 로컬 자료와 설치된 런타임만 사용해. 상위 폴더의 평가기·다른 사례는 읽거나 수정하지 마. 테스트 실패를 숨기지 말고 실제 결과와 제한을 짧게 보고해.'
        if case=='upgrade':prompt+='\n이 환경의 npm 실행 인수: '+json.dumps(npm_command(),ensure_ascii=False)
        print('START '+case,flush=True);start=time.monotonic()
        try:
            p=subprocess.run([exe,'exec','--ephemeral','--json','--sandbox','workspace-write','--skip-git-repo-check','-C',str(folder),'-'],input=prompt,text=True,encoding='utf-8',capture_output=True,timeout=420)
            write(out/(case+'-trace.jsonl'),p.stdout);write(out/(case+'-stderr.txt'),p.stderr)
            events=[json.loads(line) for line in p.stdout.splitlines()]
            completed=any(e.get('type')=='turn.completed' for e in events)
            commands=[e['item'] for e in events if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='command_execution' and e['item'].get('exit_code')==0]
            read=all(any(d.read_text(encoding='utf-8').strip().replace('\r\n','\n') in c.get('aggregated_output','').replace('\r\n','\n') for c in commands) for d in documents)
            external=any(e.get('item',{}).get('type') in ('mcp_tool_call','web_search') for e in events)
            unchanged=all(path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest()==digest for path,digest in before.items())
            v=subprocess.run([sys.executable,'-B',str(Path(__file__).resolve()),'--verify',str(folder),'--verify-case',case],capture_output=True,text=True,encoding='utf-8',timeout=120)
            write(out/(case+'-verify.txt'),v.stdout+v.stderr)
            report=json.loads(v.stdout)
            result=dict(case=case,passed=p.returncode==0 and completed and read and not external and unchanged and v.returncode==0 and report['passed'],skill_and_refs_read=read,protected_inputs_unchanged=unchanged,external_tools=external,completed=completed,exit_code=p.returncode,acceptance=report,elapsed_seconds=round(time.monotonic()-start,2),trace_sha256=hashlib.sha256(p.stdout.encode()).hexdigest())
        except subprocess.TimeoutExpired as exc:
            raw=exc.stdout or b'';raw=raw.decode('utf-8',errors='replace') if isinstance(raw,bytes) else raw
            write(out/(case+'-timeout.txt'),raw)
            result=dict(case=case,passed=False,error_type='TimeoutExpired')
        except (OSError,ValueError,KeyError,TypeError) as exc:result=dict(case=case,passed=False,error_type=type(exc).__name__)
        results.append(result);print(json.dumps(result,ensure_ascii=False),flush=True)
        write(out/'summary.json',dict(scope='native explicit skills on synthetic implementations; independent local acceptance; no production or external framework certification',cases=len(results),passed=sum(r['passed'] for r in results),results=results))
    raise SystemExit(0 if all(r['passed'] for r in results) else 1)


if __name__=='__main__':main()
