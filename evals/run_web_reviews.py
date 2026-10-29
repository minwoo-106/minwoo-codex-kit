"""Full skill execution on synthetic source and SEO snapshots; no live services."""
import argparse,hashlib,json,shutil,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
VULNERABLE='''def lookup(db, external_name):
    """external_name is the untrusted name query parameter."""
    query = "SELECT name FROM users WHERE name = '" + external_name + "'"
    return db.execute(query).fetchall()

def render(external_name):
    """This response is served as text/html to the browser."""
    return "<h1>" + external_name + "</h1>"
'''
SAFE='''import html
def lookup(db, external_name):
    return db.execute("SELECT name FROM users WHERE name = ?", (external_name,)).fetchall()
def render(external_name):
    return "<h1>" + html.escape(external_name) + "</h1>"
'''
def write(path,value):
    path.write_text(value if isinstance(value,str) else json.dumps(value,indent=2),encoding='utf-8')
def fixtures(folder,case):
    write(folder/'README.md','# Synthetic evaluation only. No user data or live service.\n')
    if case=='security':
        write(folder/'vulnerable.py',VULNERABLE);write(folder/'safe.py',SAFE)
    else:
        write(folder/'page.html','<html><head><meta name="description" content="Example"><meta name="robots" content="noindex"><script type="application/ld+json">{bad}</script></head><body>Example</body></html>')
        write(folder/'robots.txt','User-agent: *\nAllow: /\n')
        write(folder/'sitemap.xml','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://example.test/</loc></url></urlset>')
        write(folder/'manifest.json',{'pages':[{'url':'https://example.test/','html':'page.html','status':200,'headers':{},'expectIndexable':True}],'robots':'robots.txt','sitemap':'sitemap.xml'})
def verify(case,report):
    if case=='seo':
        return report.get('status')=='issues' and {x['code'] for x in report.get('findings',[])}=={'title-missing-or-multiple','unexpected-noindex','invalid-jsonld'}
    findings=report.get('findings',[])
    return (all(f.get('file')=='vulnerable.py' for f in findings) and
        any(f.get('line') in (3,4) for f in findings) and any(f.get('line') in (6,7,8) for f in findings) and
        all(isinstance(f.get('evidence'),str) and f['evidence'].strip() and isinstance(f.get('recommendation'),str) and f['recommendation'].strip() for f in findings))
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',action='store_true');p.add_argument('--out',type=Path)
    p.add_argument('--case',action='append',choices=['security','seo']);p.add_argument('--skills-root',type=Path,default=Path.home()/'.codex/skills')
    args=p.parse_args();cases=args.case or ['security','seo']
    if not args.run:print(json.dumps({'mode':'plan; no model calls','cases':cases}));return
    if not args.out:p.error('--out required')
    exe=shutil.which('codex')
    if not exe:p.error('Codex CLI required')
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);results=[]
    for case in cases:
        folder=out/case;folder.mkdir();fixtures(folder,case)
        subprocess.run(['git','init','-q',str(folder)],check=True,capture_output=True)
        before={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in folder.iterdir() if f.is_file()}
        name='minwoo-security-review' if case=='security' else 'minwoo-seo-review'
        skill=args.skills_root/name/'SKILL.md'
        task=('두 Python 파일의 앱 코드 보안을 검토해. 소스는 수정하지 말고 report.json에 findings 배열을 만들어. 각 발견은 file, line(정수), category, evidence, recommendation 필드를 가져야 해. 실제 코드에 근거한 문제만 기록해.' if case=='security' else 'manifest.json의 검색 노출 스냅샷을 제공된 검사 스크립트로 실제 점검하고 원래 JSON 결과를 report.json에 저장해. 입력과 검사 기대값은 수정하지 마.')
        prompt=f'Use $'+name+f' at {skill}.\n'+task+'\n이 폴더의 합성 자료만 사용하고 네트워크·외부 서비스는 호출하지 마. 결과 파일만 이 폴더에 만들어. 전역 설정과 승인 방식은 변경하지 마.'
        print('START '+case,flush=True);start=time.monotonic()
        proc=subprocess.run([exe,'exec','--ephemeral','--json','--sandbox','workspace-write','--skip-git-repo-check','-C',str(folder),'-'],input=prompt,capture_output=True,text=True,encoding='utf-8',timeout=300)
        write(out/(case+'-trace.jsonl'),proc.stdout);write(out/(case+'-stderr.txt'),proc.stderr)
        events=[json.loads(line) for line in proc.stdout.splitlines()]
        commands=[e['item'] for e in events if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='command_execution' and e['item'].get('exit_code')==0]
        body=skill.read_text(encoding='utf-8').replace('\r\n','\n').strip()
        read=any(body in c.get('aggregated_output','').replace('\r\n','\n') for c in commands)
        unchanged=all(hashlib.sha256((folder/name).read_bytes()).hexdigest()==digest for name,digest in before.items())
        try:report=json.loads((folder/'report.json').read_text(encoding='utf-8-sig'));artifact=verify(case,report)
        except (OSError,ValueError,KeyError,TypeError):artifact=False
        external=any(e.get('type')=='item.completed' and e.get('item',{}).get('type') in ('mcp_tool_call','web_search') for e in events)
        result={'case':case,'passed':proc.returncode==0 and read and unchanged and artifact and not external,'skill_read':read,'inputs_unchanged':unchanged,'artifact_verified':artifact,'external_tool_calls':external,'exit_code':proc.returncode,'elapsed_seconds':round(time.monotonic()-start,2),'trace_sha256':hashlib.sha256(proc.stdout.encode()).hexdigest()}
        results.append(result);print(json.dumps(result),flush=True)
        write(out/'summary.json',{'scope':'explicit skill execution on local synthetic artifacts; no production security or live SEO certification','cases':len(results),'passed':sum(x['passed'] for x in results),'results':results})
    raise SystemExit(0 if all(x['passed'] for x in results) else 1)
if __name__=='__main__':main()
