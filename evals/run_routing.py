"""Read-only native Codex routing evaluation. Default prints a plan; never installs tools."""
import argparse, hashlib, json, shutil, subprocess, time
from pathlib import Path
from run_selection import ROOT, normalize

def grade(events, documents, case):
    seen=set(); forbidden=[]; completed=False
    for event in events:
        completed |= event.get('type')=='turn.completed'
        if event.get('type')!='item.completed': continue
        item=event.get('item',{})
        if item.get('type')=='command_execution' and item.get('exit_code')==0:
            output=normalize(item.get('aggregated_output',''))
            seen.update(name for name,body in documents.items() if normalize(body) in output)
        if item.get('type') in {'file_change','mcp_tool_call','web_search'}: forbidden.append(item['type'])
    expected=set(case['routes'])|set(case['expected'])
    allowed=set(case['routes'])|set(case.get('allowed_routes',[]))|set(case['allowed'])
    return {'passed':completed and expected<=seen and seen<=allowed and not forbidden,
        'observed':sorted(seen),'missing':sorted(expected-seen),'unexpected':sorted(seen-allowed),
        'forbidden_actions':forbidden,'completed':completed}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run',action='store_true');p.add_argument('--out',type=Path)
    p.add_argument('--catalog',type=Path,help='Private JSON map of active skill names to SKILL.md paths')
    p.add_argument('--case',action='append',default=[]);p.add_argument('--timeout',type=int,default=180)
    args=p.parse_args();cases=json.loads((ROOT/'evals/routing-cases.json').read_text(encoding='utf-8'))
    if args.case:
        if set(args.case)-{c['id'] for c in cases}: p.error('unknown case')
        cases=[c for c in cases if c['id'] in args.case]
    if not args.run:
        print(json.dumps({'cases':[c['id'] for c in cases],'mode':'plan; no model calls'}));return
    if not args.out or not args.catalog: p.error('--run requires --out and --catalog')
    if not 10<=args.timeout<=600:p.error('timeout must be 10..600')
    exe=shutil.which('codex')
    if not exe:p.error('Codex CLI required')
    paths=json.loads(args.catalog.read_text(encoding='utf-8'))
    docs={name:Path(path).read_text(encoding='utf-8') for name,path in paths.items()}
    ref=ROOT/'skills/minwoo-skill-curation/references'
    docs.update({str(path.relative_to(ref)).replace('\\','/'):path.read_text(encoding='utf-8') for path in [ref/'routing.md',*sorted((ref/'routing').glob('*.md'))]})
    if any(name not in docs for c in cases for name in c['expected']):p.error('expected skill absent from supplied catalog')
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);results=[]
    version=subprocess.check_output([exe,'--version'],text=True,encoding='utf-8').strip()
    for case in cases:
        folder=out/case['id'];folder.mkdir();project=folder/'project';project.mkdir()
        fixture=project/'README.md';fixture.write_text('# Synthetic routing fixture\nNo live service, user data or production project.\n',encoding='utf-8')
        before={str(f.relative_to(project)):f.read_bytes() for f in project.rglob('*') if f.is_file()}
        prompt=case['prompt']
        if case['id']!='simple':prompt+='\n이번에는 읽기 전용 준비만 해. 관련 지침과 선택한 스킬 문서를 실제로 읽고 첫 단계만 짧게 설명해. 파일 변경, 스크립트 실행, 웹 검색, 외부 서비스 도구 호출은 하지 마.'
        command=[exe,'exec','--ephemeral','--json','--sandbox','read-only','--skip-git-repo-check','-C',str(project),'-']
        print('START '+case['id'],flush=True);started=time.monotonic()
        try:
            proc=subprocess.run(command,input=prompt,text=True,encoding='utf-8',capture_output=True,timeout=args.timeout)
            raw,error,code=proc.stdout,proc.stderr,proc.returncode
        except subprocess.TimeoutExpired as exc:
            decode=lambda v:v.decode('utf-8',errors='replace') if isinstance(v,bytes) else (v or '')
            raw,error,code=decode(exc.stdout),decode(exc.stderr),124
        (folder/'trace.jsonl').write_text(raw,encoding='utf-8');(folder/'stderr.txt').write_text(error,encoding='utf-8')
        events=[];malformed=False
        for line in raw.splitlines():
            try:events.append(json.loads(line))
            except ValueError:malformed=True
        result=grade(events,docs,case)
        after={str(f.relative_to(project)):f.read_bytes() for f in project.rglob('*') if f.is_file()}
        result.update(id=case['id'],exit_code=code,fixture_unchanged=before==after,trace_sha256=hashlib.sha256(raw.encode()).hexdigest(),elapsed_seconds=round(time.monotonic()-started,2))
        result['passed'] &= code==0 and not malformed and before==after
        results.append(result);print(('PASS ' if result['passed'] else 'FAIL ')+case['id']+' '+json.dumps(result,ensure_ascii=False),flush=True)
        summary={'cli_version':version,'model':'current user default; no override','scope':'native read-only routing and full-document read evidence; no service execution','case_count':len(results),'passed':sum(r['passed'] for r in results),'results':results,
            'guide_sha256':{name:hashlib.sha256(body.encode()).hexdigest() for name,body in docs.items() if name.startswith('routing')}}
        (out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    raise SystemExit(0 if all(r['passed'] for r in results) else 1)

if __name__=='__main__':main()
