"""Synthetic requirements and independent acceptance checks. No live accounts or data."""
import ast
import concurrent.futures
import importlib.util
import io
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tarfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

CASES = {
 'quality': ('minwoo-test-quality', 'app.py와 기존 unittest를 점검하고 경계·비활성 상태의 검증력을 보강해. 제품 구현은 바꾸지 마. python -m unittest discover 명령을 유지해.'),
 'upgrade': ('minwoo-dependency-upgrade', 'vendor의 demo-format 1.0.0을 제공된 2.0.0 tgz로 업그레이드해. MIGRATION.md를 읽고 app.cjs의 기존 trim 동작을 유지해. npm manifest/lock과 실제 호출을 바꾸고 offline npm ci와 실행을 확인해. 다른 패키지는 추가하지 마.'),
 'observability': ('minwoo-observability', 'app.py의 execute(operation, emit, clock, request_id)를 구현해. operation()을 한 번 호출하고 반환/예외를 그대로 유지해. clock()은 시작/끝 단조 초 값이다. 종료 시 event=operation, request_id, outcome=ok/error, duration_ms 네 필드만 dict로 emit에 보내. emit 오류가 결과나 원래 예외를 덮어쓰지 않게 해. 외부 exporter는 사용하지 마.'),
 'async': ('minwoo-async-jobs', 'app.py의 run_job(db, key, value, max_attempts=3, fail_first=0, cancelled=lambda:False, sleep=lambda seconds:None)를 구현해. db는 SQLite 파일 경로 문자열이다. SQLite ledger(key TEXT PRIMARY KEY, value INTEGER)에 저장하는 작업이다. 같은 키/값은 중복 적용 없이 done, 다른 값은 ValueError. value는 음수가 아닌 정수. fail_first는 커밋 전에 일시 실패할 횟수이며 attempts 상한과 주입 sleep으로 재시도해. 결과는 status(done/failed/cancelled), attempts. 이미 완료된 키는 attempts=0. 취소면 기록하지 마. 성공 기록과 부작용은 동일 SQLite 트랜잭션, 동시 호출도 중복 없어야 해. 이 fixture에는 외부 부작용이 없으며 실제 큐·프로세스 crash 검증을 주장하지 마.'),
 'state': ('minwoo-state-flow', 'app.py의 transition(state,event) 순수 함수를 구현해. state는 status idle/loading/success/error/cancelled, request_id, data 필드다. start 이벤트는 id로 loading, data=None; loading 중 중복 start는 무시. success/error는 현재 loading과 id가 같을 때만 수용, 각각 data를 event data 또는 None으로. cancel은 loading에서만 cancelled/data=None. success/error/cancelled에서도 새 start로 다시 시작할 수 있다. 늦은 응답·무효 이벤트는 무시하고 입력 dict는 수정하지 마.'),
 'data': ('minwoo-data-ingestion', 'app.py의 ingest(stream, db, stop_after=None)를 구현해. seek 가능한 UTF-8 텍스트 CSV 헤더는 id,amount,note. db는 SQLite 파일 경로 문자열이다. SQLite records(id TEXT PRIMARY KEY, amount INTEGER, note TEXT)로 적재해. amount는 음수 아닌 정수, 빈 id/잘못된 행은 거절. 같은 id/내용 중복은 추가하지 말고 다른 내용 충돌은 거절. CSV 따옴표·셀 내 줄바꿈·BOM을 지원해. 입력 SHA256과 처리 행 checkpoint를 SQLite에 저장하고 같은 입력 재호출은 재개하며 다른 입력은 ValueError로 거부해. stop_after는 이번 호출에서 읽을 데이터 행 수 상한이다. records와 checkpoint는 같은 트랜잭션으로 갱신해. 전체 파일 무제한 read는 금지하고 fingerprint 읽기는 최대8192문자 청크로 해. 반환은 processed/imported/rejected/duplicates 이번 호출 건수 dict. 원본 수정이나 외부 전송 없이 시험해.'),
 'i18n': ('minwoo-i18n', 'format.mjs를 구현해. items(locale,n)는 ko 항목 N개, en은 Intl.PluralRules로 N item/items, 지원하지 않는 locale은 en fallback. n은 음수 아닌 정수만 허용. day(iso,locale,timeZone)는 Intl.DateTimeFormat으로 해당 시간대 날짜를 반환. price(amount,locale,currency)는 Intl.NumberFormat 통화 형식. 기본 호스트 시간대에 의존하지 마. 외부 패키지·실제 번역 서비스·화면은 필요 없어.'),
 'contract': ('minwoo-api-compat', 'API 변경 뒤 기존 소비자가 깨지는 문제를 고쳐줘. api.py payload(kind)가 HTTP JSON으로 제공되고 consumer.py fetch가 실제 소비자야. ok는 기존 필수 id 문자열과 새 identifier를 함께 제공해. empty의 items=[]는 유지. 소비자 파일은 수정하지 마. 로컬 HTTP 계약 테스트를 작성하고 추가 필드 허용과 필수 필드 제거의 비호환을 확인해. Pact/Broker를 설치하거나 호출하지 마.'),
 'flaky': ('diagnosing-bugs', 'python -m unittest discover를 실행하면 테스트 순서에 따라 가끔 실패해. 원인을 재현하고 고쳐줘. add_item(item,items=None)의 기본 호출은 매번 독립 목록, 명시 목록을 주면 같은 객체에 추가해야 해. 기존 assertion·테스트 이름은 유지하고 skip이나 sleep으로 해결하지 마.'),
 'refactor': ('codebase-design', 'app.py quote(kind,units)의 중복을 정리해줘. 공개 입력·반환·오류 동작을 바꾸지 말고 기존 함수를 보존한 격리 사본과 비교해. 새 검증 규칙이나 의존성은 추가하지 마. 단순 리팩터링으로 끝내.'),
}

SOURCES = {
 'quality': {'app.py': 'def eligible(age, active):\n    return age >= 18 and active\n', 'test_app.py': 'import unittest\nfrom app import eligible\nclass Tests(unittest.TestCase):\n    def test_exists(self):\n        self.assertIsNotNone(eligible)\n'},
 'observability': {'app.py': 'def execute(operation, emit, clock, request_id):\n    return operation()\n'},
 'async': {'app.py': 'def run_job(db, key, value, max_attempts=3, fail_first=0, cancelled=lambda:False, sleep=lambda seconds:None):\n    raise NotImplementedError\n'},
 'state': {'app.py': 'def transition(state, event):\n    return state.copy()\n'},
 'data': {'app.py': 'def ingest(stream, db, stop_after=None):\n    raise NotImplementedError\n'},
 'i18n': {'format.mjs': 'export function items(locale,n) { return `${n} items`; }\nexport function day(iso,locale,timeZone) { return iso; }\nexport function price(amount,locale,currency) { return String(amount); }\n'},
 'contract': {'api.py': 'def payload(kind):\n    if kind == "empty": return {"items": []}\n    return {"identifier": "book-7"}\n', 'consumer.py': 'import json, urllib.request\ndef fetch(url,kind):\n    with urllib.request.urlopen(url+"/"+kind,timeout=3) as r: data=json.load(r)\n    if kind=="empty": return data["items"]\n    if not isinstance(data["id"],str): raise TypeError("id must be str")\n    return data["id"].upper()\n'},
 'flaky': {'app.py': 'def add_item(item, items=[]):\n    items.append(item)\n    return items\n', 'test_app.py': 'import unittest\nfrom app import add_item\nclass Tests(unittest.TestCase):\n    def test_a(self): self.assertEqual(add_item("a"),["a"])\n    def test_b(self): self.assertEqual(add_item("b"),["b"])\n'},
 'refactor': {'app.py': 'def quote(kind, units):\n    if kind == "small":\n        total = units * 3\n        if units >= 10: total -= 2\n        return total\n    if kind == "large":\n        total = units * 7\n        if units >= 10: total -= 2\n        return total\n    raise ValueError("unknown kind")\n'},
}


def command(args, cwd, timeout=45):
    p=subprocess.run(args,cwd=cwd,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=timeout)
    return p.returncode,p.stdout+p.stderr


def npm_command(*args):
    npm=shutil.which('npm.cmd') or shutil.which('npm')
    if not npm: raise RuntimeError('npm required for upgrade fixture')
    # Portable bundled npm wrappers may assume a different Node installation layout.
    cli=Path(npm).resolve().parent/'npm-cli.js'
    if cli.is_file():return [shutil.which('node') or 'node',str(cli),*args]
    return [npm,*args]


def setup(folder,case):
    for name,body in SOURCES.get(case,{}).items(): (folder/name).write_text(body,encoding='utf-8')
    (folder/'README.md').write_text('# Synthetic coding fixture\nNo production data or services.\n',encoding='utf-8')
    if case=='upgrade':
        vendor=folder/'vendor';vendor.mkdir()
        for version,code in [('1.0.0','exports.format = value => String(value).trim();'),('2.0.0','exports.format = options => { if (!options || typeof options !== "object") throw new TypeError("options required"); return String(options.value).trim(); };')]:
            with tarfile.open(vendor/f'demo-format-{version}.tgz','w:gz') as tar:
                for name,body in [('package.json',json.dumps({'name':'demo-format','version':version,'main':'index.cjs'})),('index.cjs',code)]:
                    data=body.encode();info=tarfile.TarInfo('package/'+name);info.size=len(data);tar.addfile(info,io.BytesIO(data))
        (folder/'package.json').write_text(json.dumps({'name':'synthetic-upgrade','version':'1.0.0','private':True,'dependencies':{'demo-format':'file:vendor/demo-format-1.0.0.tgz'}}),encoding='utf-8')
        (folder/'app.cjs').write_text('const {format}=require("demo-format"); exports.label = value => format(value);\n',encoding='utf-8')
        (folder/'MIGRATION.md').write_text('Synthetic release 2.0.0: format(value) became format({value}). Output remains String(value).trim(). Local tarballs only; no registry requests.\n',encoding='utf-8')
        code,output=command(npm_command('install','--package-lock-only','--ignore-scripts','--offline','--no-audit','--no-fund'),folder)
        if code:
            (folder/'setup-error.txt').write_text(output,encoding='utf-8')
            raise RuntimeError('offline lock creation failed; local setup-error.txt retained')
    subprocess.run(['git','init','-q',str(folder)],capture_output=True,check=True)


def module(folder,name='app'):
    spec=importlib.util.spec_from_file_location('fixture_'+name,folder/(name+'.py'))
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def original_tests_preserved(before,after):
    """Allow added regression tests, but preserve original test bodies and decorators."""
    try:
        original=ast.parse(before);current=ast.parse(after)
        old=next(n for n in original.body if isinstance(n,ast.ClassDef) and n.name=='Tests')
        candidates=[n for n in current.body if isinstance(n,ast.ClassDef) and n.name=='Tests']
        if len(candidates)!=1:return False
        new=candidates[0]
        if ast.dump(ast.Module(body=new.decorator_list,type_ignores=[]))!=ast.dump(ast.Module(body=old.decorator_list,type_ignores=[])):return False
        if [ast.dump(n) for n in old.bases]!=[ast.dump(n) for n in new.bases]:return False
        for fn in [n for n in old.body if isinstance(n,ast.FunctionDef)]:
            matches=[n for n in new.body if isinstance(n,ast.FunctionDef) and n.name==fn.name]
            if len(matches)!=1 or ast.dump(fn)!=ast.dump(matches[0]):return False
        return True
    except (SyntaxError,StopIteration):return False


def verify(folder,case):
    checks=[]
    def check(label,condition):
        checks.append({'name':label,'passed':bool(condition)})
    def raises(fn,kind=Exception):
        try:fn();return False
        except kind:return True
    if case=='quality':
        app=folder/'app.py';original=app.read_text(encoding='utf-8')
        check('implementation unchanged',original==SOURCES['quality']['app.py'])
        check('normal tests pass',command([sys.executable,'-B','-m','unittest','discover'],folder)[0]==0)
        try:
            for name,expr in [('age boundary','age > 18 and active'),('wrong connective','age >= 18 or active'),('always true','True')]:
                app.write_text('def eligible(age, active):\n    return '+expr+'\n',encoding='utf-8')
                check('detect '+name,command([sys.executable,'-B','-m','unittest','discover'],folder)[0]!=0)
        finally:app.write_text(original,encoding='utf-8')
    elif case=='upgrade':
        check('offline clean install',command(npm_command('ci','--ignore-scripts','--offline','--no-audit','--no-fund'),folder)[0]==0)
        code,_=command(['node','-e','const a=require("./app.cjs"); const assert=require("node:assert/strict"); assert.equal(a.label("  hello  "),"hello"); assert.equal(a.label(42),"42"); assert.equal(require("demo-format/package.json").version,"2.0.0");'],folder)
        check('v2 real API preserves behavior',code==0)
        manifest=json.loads((folder/'package.json').read_text());lock=json.loads((folder/'package-lock.json').read_text())
        check('manifest lock consistent',manifest['dependencies']==lock['packages']['']['dependencies'])
        check('only intended dependency',set(manifest['dependencies'])=={'demo-format'})
    elif case=='observability':
        f=module(folder).execute;events=[];times=iter([1,1.25]);calls=[]
        result=f(lambda:(calls.append(1) or 7),events.append,lambda:next(times),'req-1')
        check('result and single call',result==7 and calls==[1])
        check('bounded fields and timing',len(events)==1 and events[0]==dict(event='operation',request_id='req-1',outcome='ok',duration_ms=250))
        error=ValueError('private input example');times=iter([2,2.1]);events=[]
        def fail():raise error
        try:f(fail,events.append,lambda:next(times),'req-2');same=False
        except ValueError as e:same=e is error
        check('original error and redacted event',same and len(events)==1 and events[0]['outcome']=='error' and 'private' not in json.dumps(events))
        def bad_sink(e):raise RuntimeError('sink down')
        times=iter([3,4]);check('sink failure preserves success',f(lambda:8,bad_sink,lambda:next(times),'req-3')==8)
        times=iter([4,5])
        try:f(fail,bad_sink,lambda:next(times),'req-4');same=False
        except ValueError as e:same=e is error
        check('sink failure preserves original error',same)
    elif case=='async':
        f=module(folder).run_job;db=str(folder/'acceptance-jobs.sqlite');sleeps=[]
        r=f(db,'a',5,fail_first=2,sleep=sleeps.append);check('bounded retry then success',r['status']=='done' and r['attempts']==3 and len(sleeps)==2)
        check('duplicate has no attempts',f(db,'a',5)['attempts']==0)
        check('same key different content rejected',raises(lambda:f(db,'a',6),ValueError))
        check('permanent invalid input',raises(lambda:f(db,'negative',-1),ValueError))
        r=f(db,'bad',2,max_attempts=2,fail_first=9);check('retry exhaustion',r['status']=='failed' and r['attempts']==2)
        check('cancelled',f(db,'cancel',2,cancelled=lambda:True)['status']=='cancelled')
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(lambda _:f(db,'parallel',9),range(4)))
        with sqlite3.connect(db) as c:rows=c.execute('SELECT key,value FROM ledger ORDER BY key').fetchall()
        check('atomic duplicate application',rows==[('a',5),('parallel',9)] and all(r['status']=='done' for r in results))
    elif case=='state':
        f=module(folder).transition;s=dict(status='idle',request_id=None,data=None);original=s.copy();a=f(s,{'type':'start','id':'1'})
        check('pure start',s==original and a==dict(status='loading',request_id='1',data=None))
        check('duplicate start ignored',f(a,{'type':'start','id':'2'})==a)
        c=f(a,{'type':'cancel'});check('cancel active',c['status']=='cancelled' and c['data'] is None)
        check('late success ignored',f(c,{'type':'success','id':'1','data':'old'})==c)
        b=f(c,{'type':'start','id':'2'});check('stale generation ignored',f(b,{'type':'success','id':'1','data':'old'})==b)
        done=f(b,{'type':'success','id':'2','data':'new'});check('matching result',done['status']=='success' and done['data']=='new')
        e=f(f(done,{'type':'start','id':'3'}),{'type':'error','id':'3'});check('error transition',e['status']=='error' and e['data'] is None)
        check('unknown ignored',f(e,{'type':'other'})==e)
    elif case=='data':
        f=module(folder).ingest;db=str(folder/'acceptance-data.sqlite')
        data='\ufeffid,amount,note\na,2,"two\nlines"\nb,broken,x\na,2,"two\nlines"\nc,4,last\n'
        class Bounded(io.StringIO):
            def read(self,n=-1):
                if not 0<=n<=8192:raise AssertionError('unbounded read')
                return super().read(n)
        first=f(Bounded(data),db,stop_after=2);second=f(Bounded(data),db);third=f(Bounded(data),db)
        check('first batch partial counts',first==dict(processed=2,imported=1,rejected=1,duplicates=0))
        check('resume counts',second==dict(processed=2,imported=1,rejected=0,duplicates=1))
        check('completed repeat no work',third==dict(processed=0,imported=0,rejected=0,duplicates=0))
        check('input change refused',raises(lambda:f(Bounded(data+'d,7,x\n'),db),ValueError))
        with sqlite3.connect(db) as c:rows=c.execute('SELECT id,amount,note FROM records ORDER BY id').fetchall()
        check('multiline and checkpoint persist',rows==[('a',2,'two\nlines'),('c',4,'last')])
        large='id,amount,note\n'+''.join(f'{i},1,x\n' for i in range(10000))
        check('bounded reading 10000 records',f(Bounded(large),str(folder/'acceptance-large.sqlite'))['imported']==10000)
    elif case=='i18n':
        code='''import assert from 'node:assert/strict'; import {items,day,price} from './format.mjs';
assert.equal(items('en',1),'1 item'); assert.equal(items('en',0),'0 items'); assert.equal(items('en',2),'2 items');
assert.equal(items('ko',2),'항목 2개'); assert.equal(items('xx',2),'2 items'); assert.throws(()=>items('en',-1));
for(const [locale,zone] of [['en-US','Asia/Seoul'],['en-US','America/Los_Angeles']]) {
 const d='2026-01-01T01:00:00Z'; const s=day(d,locale,zone); const expected=new Intl.DateTimeFormat(locale,{timeZone:zone}).format(new Date(d)); assert.equal(s,expected);
}
assert.equal(price(1234,'en-US','USD'),new Intl.NumberFormat('en-US',{style:'currency',currency:'USD'}).format(1234));
assert.equal(price(1234,'ko-KR','KRW'),new Intl.NumberFormat('ko-KR',{style:'currency',currency:'KRW'}).format(1234));'''
        code_ret,_=command(['node','--input-type=module','-e',code],folder)
        check('plural fallback date boundary and currency',code_ret==0)
    elif case=='contract':
        provider=module(folder,'api');consumer=module(folder,'consumer');mode=['normal']
        class Handler(BaseHTTPRequestHandler):
            def log_message(self,*args):pass
            def do_GET(self):
                value=provider.payload(self.path.lstrip('/'))
                if mode[0]=='extra':value={**value,'unrelated':123}
                if mode[0]=='broken':value={k:v for k,v in value.items() if k!='id'}
                self.send_response(200);self.end_headers();self.wfile.write(json.dumps(value).encode())
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            url=f'http://127.0.0.1:{server.server_port}'
            check('real consumer HTTP normal',consumer.fetch(url,'ok')=='BOOK-7')
            check('new field retained',provider.payload('ok')['identifier']=='book-7')
            check('empty semantics',consumer.fetch(url,'empty')==[])
            mode[0]='extra';check('additional fields compatible',consumer.fetch(url,'ok')=='BOOK-7')
            mode[0]='broken';check('missing field is incompatible',raises(lambda:consumer.fetch(url,'ok'),KeyError))
        finally:server.shutdown();server.server_close()
        check('consumer preserved',(folder/'consumer.py').read_text(encoding='utf-8')==SOURCES['contract']['consumer.py'])
    elif case=='flaky':
        f=module(folder).add_item;check('independent defaults',f('a')==['a'] and f('b')==['b'])
        target=[];check('explicit list identity',f('x',target) is target and target==['x'])
        check('original tests preserved',original_tests_preserved(SOURCES['flaky']['test_app.py'],(folder/'test_app.py').read_text(encoding='utf-8')))
        check('full regression suite',command([sys.executable,'-B','-m','unittest','discover'],folder)[0]==0)
        for order in [('test_a','test_b'),('test_b','test_a')]:check('order '+','.join(order),command([sys.executable,'-B','-m','unittest',*['test_app.Tests.'+n for n in order]],folder)[0]==0)
    elif case=='refactor':
        old={};exec(SOURCES['refactor']['app.py'],old);f=module(folder).quote
        def outcome(fn,k,v):
            try:return ('value',fn(k,v))
            except Exception as e:return (type(e).__name__,str(e))
        inputs=[(kind,n) for kind in ('small','large','unknown') for n in (-10,0,1,9,10,11,100,False,True,1.5,None,'2')]
        check('36 behavior comparisons',all(outcome(f,k,v)==outcome(old['quote'],k,v) for k,v in inputs))
        check('implementation actually changed',(folder/'app.py').read_text(encoding='utf-8')!=SOURCES['refactor']['app.py'])
    return checks
