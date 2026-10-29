"""Explicit skill execution in fresh Codex sessions; verify produced artifacts independently."""
import argparse
import functools
import hashlib
import http.server
import json
from pathlib import Path
import shutil
import subprocess
import sys
import threading
import time
import zipfile
from practical_fixtures import create,write,ROOT

CASES={'browser':('minwoo-browser-check','check_browser.mjs'),
       'api':('minwoo-api-compat','check_contract.py'),
       'video':('minwoo-video-review','check_delivery.py'),
       'migration':('minwoo-postgres-review','rehearse.mjs'),
       'ci':('diagnosing-bugs','unittest')}

def hashes(folder):
    return {p.relative_to(folder).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for p in folder.rglob('*') if p.is_file() and not {'__pycache__','.git'}.intersection(p.parts)}

def verify(case,folder):
    if case=='ci':
        command=[sys.executable,'-B','-c',
            'from app import ratio; assert ratio(7,2)==3.5; assert ratio(-3,2)==-1.5; assert ratio(6,2)==3']
        return subprocess.run(command,cwd=folder,capture_output=True,timeout=20).returncode==0
    report=json.loads((folder/('evidence/report.json' if case=='browser' else 'report.json')).read_text(encoding='utf-8-sig'))
    if case=='api': return report.get('counts',{}).get('breaking')==3 and report.get('status')=='breaking'
    if case=='video': return report.get('passed') is False and set(report.get('failures',[]))=={'audio','fps','SRT outside media duration or empty interval'}
    if case=='migration': return report.get('passed') is False and report.get('failed_stage')=='after'
    if case=='browser':
        screenshot=folder/'evidence/1/screenshot.png'; trace=folder/'evidence/1/trace.zip'
        with zipfile.ZipFile(trace) as archive:
            valid=archive.testzip() is None and any(n.endswith('.trace') for n in archive.namelist())
        return report.get('passed') is False and report['cases'][0].get('failed_step')==3 and valid and screenshot.read_bytes().startswith(b'\x89PNG')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run',action='store_true');p.add_argument('--out',type=Path)
    p.add_argument('--runtime',type=Path);p.add_argument('--browser');p.add_argument('--case',action='append')
    p.add_argument('--skills-root',type=Path,default=Path.home()/'.codex/skills')
    args=p.parse_args();cases=args.case or list(CASES)
    if set(cases)-set(CASES): p.error('unknown case')
    if not args.run: print(json.dumps({'mode':'plan; no model calls','cases':cases}));return
    if not args.out or not args.runtime: p.error('--out --runtime required')
    executable=shutil.which('codex')
    if not executable: p.error('Codex CLI required')
    destination=args.out.resolve();destination.mkdir(parents=True,exist_ok=False)
    fixtures=destination/'fixtures';info=create(fixtures,args.runtime.resolve())
    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self,*a): pass
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(QuietHandler,directory=str(fixtures/'browser')))
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    base='http://127.0.0.1:'+str(server.server_port)
    write(fixtures/'browser/scenario.json',{'baseURL':base,'cases':[{'name':'search','steps':[
        {'action':'goto','path':'/bad.html'},{'action':'fill','testId':'query','value':'apple'},
        {'action':'click','role':'button','name':'Search'},{'action':'text','testId':'result','value':'apple'}]}]})
    tasks={
      'browser':'scenario.json에 있는 검색 동작을 제공 실행기로 실제 검사해. 기대 동작을 바꾸거나 앱을 고치지 말고 evidence 폴더에 검사 결과·스크린샷·trace를 만들어.',
      'api':'before.json과 after.json의 API 호환성을 제공 비교기로 검사하고 원래 JSON 결과를 report.json에 저장해. 명세는 수정하지 마.',
      'video':'sample.mp4를 spec.json 규격과 bad.srt 자막으로 제공 도구를 이용해 점검하고 원래 JSON 결과를 report.json에 저장해. 원본·규격은 수정하지 마.',
      'migration':'setup.sql, up.sql, checks.json, down.sql로 제공 격리 도구를 실행해 데이터 보존과 복구 가능성을 점검하고 원래 JSON 결과를 report.json에 저장해. SQL·기대값을 수정하지 마.',
      'ci':'ci.log의 실패를 로컬에서 재현하고 app.py의 원인을 고친 뒤 기존 테스트로 검증해. test_app.py나 기대값은 바꾸지 마. 로그는 합성 자료이며 GitHub 원격 조회·푸시·CI 재실행은 하지 마.'
    }
    results=[]
    try:
        for case in cases:
            folder=fixtures/case;name,helper=CASES[case]
            subprocess.run(['git','init','-q',str(folder)],check=True,capture_output=True)
            skill=args.skills_root/name/'SKILL.md'
            before=hashes(folder)
            prefailed=True
            if case=='ci': prefailed=subprocess.run([sys.executable,'-B','-m','unittest','-v'],cwd=folder,capture_output=True).returncode!=0
            prompt=(f'이 합성 프로젝트에서 $'+name+f' 스킬({skill})을 읽고 작업해. '+tasks[case]+
                f'\n설치된 도구 런타임: {args.runtime.resolve()}\n브라우저 실행 파일: {args.browser or "기본 Chromium"}\nffprobe: {info["ffprobe"]}\n'+
                '이 작업 폴더 안에서 필요한 결과물을 만들거나 지정한 버그를 고치는 권한은 이미 있어. 설정·승인 방식·다른 파일·외부 서비스는 변경하지 마. 도구가 결함을 발견해 종료 코드 1을 반환하면 그 사실을 보고해. 실제 수행한 결과만 짧게 설명해.')
            print('START '+case,flush=True);start=time.monotonic()
            try:
                proc=subprocess.run([executable,'exec','--ephemeral','--json','--sandbox','workspace-write','--skip-git-repo-check','-C',str(folder),'-'],
                    input=prompt,capture_output=True,text=True,encoding='utf-8',timeout=300)
                raw,error,code=proc.stdout,proc.stderr,proc.returncode
            except subprocess.TimeoutExpired as e:
                raw=e.stdout or b'';error=e.stderr or b'';code=124
                if isinstance(raw,bytes):raw=raw.decode('utf-8',errors='replace')
                if isinstance(error,bytes):error=error.decode('utf-8',errors='replace')
            (destination/(case+'.jsonl')).write_text(raw,encoding='utf-8')
            (destination/(case+'.stderr')).write_text(error,encoding='utf-8')
            events=[]
            for line in raw.splitlines():
                try:events.append(json.loads(line))
                except ValueError:pass
            commands=[e['item'] for e in events if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='command_execution']
            body=skill.read_text(encoding='utf-8').replace('\r\n','\n').strip()
            loaded=any(c.get('exit_code')==0 and body in c.get('aggregated_output','').replace('\r\n','\n') for c in commands)
            used=any(helper in c.get('command','') for c in commands)
            after=hashes(folder)
            preserved=all(after.get(n)==h for n,h in before.items() if not(case=='ci' and n=='app.py'))
            try:artifact_ok=verify(case,folder)
            except (OSError,ValueError,KeyError,IndexError,zipfile.BadZipFile,subprocess.SubprocessError):artifact_ok=False
            completed=any(e.get('type')=='turn.completed' for e in events)
            result={'case':case,'passed':code==0 and loaded and used and preserved and artifact_ok and prefailed and completed,
                    'skill_read':loaded,'tool_command_seen':used,'inputs_preserved':preserved,'artifact_verified':artifact_ok,
                    'completed':completed,'exit_code':code,'elapsed_seconds':round(time.monotonic()-start,2),
                    'trace_sha256':hashlib.sha256(raw.encode()).hexdigest()}
            results.append(result);print(json.dumps(result),flush=True)
            summary={'scope':'explicit skill execution and independently checked synthetic artifacts; raw traces remain private',
                'cases':len(results),'passed':sum(x['passed'] for x in results),'results':results}
            (destination/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    finally:server.shutdown();server.server_close();thread.join()
    raise SystemExit(0 if all(x['passed'] for x in results) else 1)

if __name__=='__main__':main()
