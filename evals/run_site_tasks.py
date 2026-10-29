"""Run native Codex skills on synthetic website briefs; review creative artifacts separately."""
import argparse,hashlib,json,shutil,subprocess,threading,time
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path

def write(path,data):path.write_text(data if isinstance(data,str) else json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
def fixture(folder,case,base_url):
    facts={'name':'책쉼','audience':'동네 독립서점 운영자','service':'예약한 시간에 책 소개 사진을 촬영','price_won':65000,'session_minutes':20,'delivery':'보정 사진 5장','contact_action':'문의 접수, 예약 확정 아님','voice':'차분하고 다정한 존댓말','unknown':['촬영 가능 지역','납품 소요 시간'],'not_provided':['고객 수','후기','수상','할인','무료 상담']}
    write(folder/'facts.json',facts)
    write(folder/'README.md','# Synthetic fixture only. No real business, users or accounts.\n')
    if case=='assets':
        write(folder/'hero.svg','<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="600"><rect width="1200" height="600" fill="#204030"/></svg>')
        write(folder/'font.bin','SYNTHETIC FONT PLACEHOLDER - NOT A REAL FONT')
        write(folder/'assets.json',{'assets':[{'file':'hero.svg','source':'이번 합성 시험에서 직접 만든 도형','intended_display':[600,300]},{'file':'font.bin','source':'알 수 없음','license':'제공되지 않음'}]})
    if case=='launch':
        write(folder/'site.json',{'baseURL':base_url,'cases':[{'name':'home','path':'/'}],'linkPaths':['/missing']})

def verify(case,report,folder):
    if case=='brand-copy':return isinstance(report.get('voice'),dict) and bool(report['voice']) and isinstance(report.get('copy'),dict) and bool(report['copy'])
    if case=='brief':return isinstance(report.get('pages'),list) and bool(report['pages']) and isinstance(report.get('unknowns'),list) and bool(report['unknowns'])
    if case=='assets':
        entries=report.get('assets',[])
        return ({e.get('file') for e in entries}=={'hero.svg','font.bin'} and all(e.get('bytes')==(folder/e['file']).stat().st_size for e in entries) and any(e['file']=='font.bin' and e.get('rights_status')=='unknown' for e in entries))
    return report.get('status')=='issues' and any(l.get('status')==404 and not l.get('passed') for l in report.get('links',[]))

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def do_GET(self):
        self.send_response(200 if self.path=='/' else 404);self.send_header('Content-Type','text/html; charset=utf-8');self.end_headers()
        self.wfile.write(b'<html><head><title>Fixture</title></head><body><h1>Fixture</h1><a href="/missing">Details</a></body></html>')

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--run',action='store_true');parser.add_argument('--out',type=Path);parser.add_argument('--case',action='append',choices=['brand-copy','brief','assets','launch']);parser.add_argument('--runtime',type=Path);parser.add_argument('--browser',type=Path)
    args=parser.parse_args();cases=args.case or ['brand-copy','brief','assets','launch']
    if not args.run:print(json.dumps({'mode':'plan; no model calls','cases':cases}));return
    if not args.out:parser.error('--out required')
    if 'launch' in cases and not args.runtime:parser.error('--runtime required for launch')
    executable=shutil.which('codex')
    if not executable:parser.error('Codex CLI required')
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    skills=Path.home()/'.codex/skills';results=[]
    try:
        for case in cases:
            folder=out/case;folder.mkdir();fixture(folder,case,f'http://127.0.0.1:{server.server_port}')
            subprocess.run(['git','init','-q',str(folder)],check=True,capture_output=True)
            before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.iterdir() if p.is_file()}
            names={'brand-copy':['minwoo-brand-voice','minwoo-web-copy'],'brief':['minwoo-project-context'],'assets':['minwoo-web-assets'],'launch':['minwoo-web-launch']}[case]
            task={
              'brand-copy':'facts.json을 근거로 짧은 브랜드 말투 가이드와 홈페이지 첫 화면·서비스 설명·FAQ·문의 버튼 문구를 작성해. report.json에 voice 객체와 copy 객체로 저장해. 최종 문구와 미확정 사항을 구분해.',
              'brief':'facts.json의 서비스 홈페이지를 기획해. report.json에 pages 배열과 unknowns 배열로 저장해. 페이지별 목적·콘텐츠·다음 행동을 포함해. 브랜드 문구 작성이나 UI 구현은 하지 마.',
              'assets':'assets.json과 실제 두 파일을 점검해. report.json의 assets 배열에 file, bytes(실측), rights_status(known 또는 unknown), notes를 기록해. 파일 수정·변환이나 이미지 생성은 하지 마.',
              'launch':f'site.json의 로컬 사이트를 실제로 검사해. 설치된 minwoo-browser-check/scripts/inspect_site.mjs 도구, runtime={args.runtime}, browser={args.browser}를 사용하고 원래 JSON 결과를 report.json에도 저장해. 검사 실패를 성공으로 바꾸지 마. 배포는 하지 마.'
            }[case]
            prompt='\n'.join('Use $'+name+' at '+str(skills/name/'SKILL.md') for name in names)+'\n'+task+'\n합성 자료만 사용하고 입력·전역 설정·승인 방식을 수정하지 마. 외부 서비스·웹 검색을 호출하지 마. 로컬 테스트 URL과 이 폴더만 작업 대상으로 사용해.'
            print('START '+case,flush=True);start=time.monotonic()
            try:
                proc=subprocess.run([executable,'exec','--ephemeral','--json','--sandbox','workspace-write','--skip-git-repo-check','-C',str(folder),'-'],input=prompt,text=True,encoding='utf-8',capture_output=True,timeout=300)
                write(out/(case+'-trace.jsonl'),proc.stdout);write(out/(case+'-stderr.txt'),proc.stderr)
                events=[json.loads(line) for line in proc.stdout.splitlines()]
                commands=[e['item'] for e in events if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='command_execution' and e['item'].get('exit_code')==0]
                read=all(any((skills/name/'SKILL.md').read_text(encoding='utf-8').strip().replace('\r\n','\n') in c.get('aggregated_output','').replace('\r\n','\n') for c in commands) for name in names)
                report=json.loads((folder/'report.json').read_text(encoding='utf-8-sig'));artifact=verify(case,report,folder)
                helper=case!='launch' or any('inspect_site.mjs' in e.get('item',{}).get('command','') for e in events)
                unchanged=all((folder/n).is_file() and hashlib.sha256((folder/n).read_bytes()).hexdigest()==h for n,h in before.items())
                external=any(e.get('type')=='item.completed' and e.get('item',{}).get('type') in ('mcp_tool_call','web_search') for e in events)
                result={'case':case,'passed':proc.returncode==0 and read and artifact and helper and unchanged and not external,'skill_read':read,'artifact_verified':artifact,'helper_executed':helper if case=='launch' else None,'inputs_unchanged':unchanged,'external_tools':external,'exit_code':proc.returncode,'elapsed_seconds':round(time.monotonic()-start,2),'trace_sha256':hashlib.sha256(proc.stdout.encode()).hexdigest()}
            except (OSError,ValueError,KeyError,TypeError,subprocess.TimeoutExpired) as e:result={'case':case,'passed':False,'error_type':type(e).__name__}
            results.append(result);print(json.dumps(result),flush=True)
            write(out/'summary.json',{'scope':'explicit skills on synthetic artifacts; creative quality and factual claims need manual review; not conversion or audience testing','cases':len(results),'passed':sum(r['passed'] for r in results),'results':results})
    finally:server.shutdown();server.server_close()
    raise SystemExit(0 if all(r['passed'] for r in results) else 1)
if __name__=='__main__':main()
